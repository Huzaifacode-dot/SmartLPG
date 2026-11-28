import os
import sys

# Ensure root directory is on sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import random
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

from backend.database import get_db_connection, init_db
from backend.ml_model import predict_consumption, predict_multi_factor_consumption, compute_refill_analytics
from backend.iot_simulator import IoTSimulator

# Base directories
TEMPLATE_DIR = os.path.join(BASE_DIR, "frontend", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
CORS(app)

# Ensure DB is initialized
init_db()

# ----------------- WEB PAGES & STATIC ASSETS -----------------
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "SmartLPG API",
        "db_connected": True
    }), 200

@app.route("/")
@app.route("/index.html")
@app.route("/api")
@app.route("/api/index")
def index():
    return render_template("index.html")

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory(STATIC_DIR, filename)

@app.route("/css/<path:filename>")
def serve_css(filename):
    return send_from_directory(os.path.join(STATIC_DIR, "css"), filename)

@app.route("/js/<path:filename>")
def serve_js(filename):
    return send_from_directory(os.path.join(STATIC_DIR, "js"), filename)

# ----------------- USER PROFILE APIs -----------------
@app.route("/api/profile", methods=["GET"])
def get_profile():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_profile ORDER BY id ASC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        data = dict(row)
        defaults = {
            "distributor_phone": "+91 80 2520 1199",
            "connection_type": "14.2 kg Subsidized Domestic (Single Cylinder)",
            "adults_count": 2,
            "children_count": 2,
            "usage_purpose": "Household",
            "household_classification": "Family Household",
            "date_of_last_refill": "2026-10-12",
            "current_refill_price": 858.00,
            "cooking_days_per_week": 7,
            "avg_time_per_meal": "20 Minutes (Quick)",
            "flame_intensity": "Medium Flame",
            "frequently_cooked_foods": "Rice,Soup,Stew,Water & Tea Boiling",
            "extra_appliances": "",
            "extra_weekly_hours": 0.0,
            "use_pressure_cooker": 1,
            "use_saving_lids": 1,
            "cook_in_batches": 1,
            "reheat_on_stove": 0
        }
        for k, v in defaults.items():
            if k not in data or data[k] is None:
                data[k] = v
        return jsonify(data)
    return jsonify({"error": "Profile not found"}), 404

@app.route("/api/profile", methods=["PUT"])
@app.route("/api/profile/details-update", methods=["POST", "PUT"])
def update_profile():
    try:
        data = request.json or {}
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM user_profile ORDER BY id ASC LIMIT 1")
        user = cursor.fetchone()
        if not user:
            from backend.database import seed_initial_data
            seed_initial_data(conn)
            cursor.execute("SELECT * FROM user_profile ORDER BY id ASC LIMIT 1")
            user = cursor.fetchone()
            if not user:
                conn.close()
                return jsonify({"error": "Profile not found and could not be initialized", "status": "failed"}), 404

        cursor.execute("PRAGMA table_info(user_profile)")
        rows = cursor.fetchall()
        existing_cols = {row["name"] if hasattr(row, "keys") else row[1] for row in rows}

        allowed_fields = [
            "primary_name", "phone", "email", "address", "lpg_provider", "consumer_number",
            "distributor_name", "distributor_phone", "connection_type",
            "family_size", "adults_count", "children_count", "cooking_meals_per_day",
            "daily_cooking_hours", "usage_purpose", "household_classification",
            "cylinder_capacity", "date_of_last_refill", "current_refill_price", "lead_time_days",
            "cooking_days_per_week", "avg_time_per_meal", "flame_intensity",
            "frequently_cooked_foods", "extra_appliances", "extra_weekly_hours",
            "use_pressure_cooker", "use_saving_lids", "cook_in_batches", "reheat_on_stove"
        ]
        
        # Calculate family size if adults/children passed
        if "adults_count" in data or "children_count" in data:
            ad = int(data.get("adults_count", user["adults_count"] if "adults_count" in user.keys() else 2))
            ch = int(data.get("children_count", user["children_count"] if "children_count" in user.keys() else 2))
            data["family_size"] = ad + ch
            
        update_fields = {}
        for field in allowed_fields:
            if field in data and field in existing_cols:
                val = data[field]
                if field in ["family_size", "adults_count", "children_count", "cooking_meals_per_day", "lead_time_days",
                             "cooking_days_per_week", "use_pressure_cooker", "use_saving_lids", "cook_in_batches", "reheat_on_stove"]:
                    val = int(val)
                elif field in ["daily_cooking_hours", "cylinder_capacity", "current_refill_price", "extra_weekly_hours"]:
                    val = float(val)
                elif isinstance(val, list):
                    val = ",".join(str(item) for item in val)
                update_fields[field] = val

        if update_fields:
            set_clause = ", ".join([f"{k} = ?" for k in update_fields.keys()])
            params = list(update_fields.values()) + [user["id"]]
            cursor.execute(f"UPDATE user_profile SET {set_clause} WHERE id = ?", params)
        
        # Recalculate burn rate with all 5 Multi-Factor Steps
        adults = int(data.get("adults_count", user["adults_count"] if "adults_count" in user.keys() else 2))
        children = int(data.get("children_count", user["children_count"] if "children_count" in user.keys() else 2))
        meals = int(data.get("cooking_meals_per_day", user["cooking_meals_per_day"]))
        days_week = int(data.get("cooking_days_per_week", user["cooking_days_per_week"] if "cooking_days_per_week" in user.keys() else 7))
        avg_mins = data.get("avg_time_per_meal", user["avg_time_per_meal"] if "avg_time_per_meal" in user.keys() else "20 Minutes (Quick)")
        flame = data.get("flame_intensity", user["flame_intensity"] if "flame_intensity" in user.keys() else "Medium Flame")
        foods = data.get("frequently_cooked_foods", user["frequently_cooked_foods"] if "frequently_cooked_foods" in user.keys() else "Rice,Soup,Stew")
        extra_apps = data.get("extra_appliances", user["extra_appliances"] if "extra_appliances" in user.keys() else "")
        extra_hrs = float(data.get("extra_weekly_hours", user["extra_weekly_hours"] if "extra_weekly_hours" in user.keys() else 0.0))
        p_cooker = bool(int(data.get("use_pressure_cooker", user["use_pressure_cooker"] if "use_pressure_cooker" in user.keys() else 1)))
        lids = bool(int(data.get("use_saving_lids", user["use_saving_lids"] if "use_saving_lids" in user.keys() else 1)))
        batches = bool(int(data.get("cook_in_batches", user["cook_in_batches"] if "cook_in_batches" in user.keys() else 1)))
        reheat = bool(int(data.get("reheat_on_stove", user["reheat_on_stove"] if "reheat_on_stove" in user.keys() else 0)))
        cap = float(data.get("cylinder_capacity", user["cylinder_capacity"] if "cylinder_capacity" in user.keys() else 14.2))

        burn_rate = predict_multi_factor_consumption(
            adults_count=adults,
            children_count=children,
            meals_per_day=meals,
            cooking_days_per_week=days_week,
            avg_meal_minutes=avg_mins,
            flame_intensity=flame,
            foods_cooked=foods,
            extra_appliances=extra_apps,
            extra_weekly_hours=extra_hrs,
            use_pressure_cooker=p_cooker,
            use_saving_lids=lids,
            cook_in_batches=batches,
            reheat_on_stove=reheat,
            cylinder_capacity=cap
        )
        
        # Update active cylinder burn rate and days remaining
        cursor.execute("SELECT * FROM cylinder_status ORDER BY id DESC LIMIT 1")
        cyl = cursor.fetchone()
        days_rem = 0.0
        if cyl:
            days_rem = round(cyl["current_gas_weight"] / burn_rate, 1) if burn_rate > 0 else 0
            pred_empty = (datetime.now() + timedelta(days=days_rem)).strftime("%Y-%m-%d")
            cursor.execute('''
            UPDATE cylinder_status SET
                burn_rate_kg_per_day = ?,
                days_remaining = ?,
                predicted_empty_date = ?
            WHERE id = ?
            ''', (burn_rate, days_rem, pred_empty, cyl["id"]))
        else:
            installed_date = (datetime.now() - timedelta(days=28)).strftime("%Y-%m-%d")
            days_rem = round(14.2 / burn_rate, 1)
            pred_empty = (datetime.now() + timedelta(days=days_rem)).strftime("%Y-%m-%d")
            cursor.execute('''
            INSERT INTO cylinder_status (
                cylinder_serial, installed_date, tare_weight, initial_gas_weight,
                current_gas_weight, burn_rate_kg_per_day, predicted_empty_date, days_remaining,
                status, is_leak_detected, iot_sync_enabled
            ) VALUES ('IND-BLR-2026-9921', ?, 15.30, 14.20, 14.20, ?, ?, ?, 'ACTIVE', 0, 1)
            ''', (installed_date, burn_rate, pred_empty, days_rem))

        cursor.execute('''
        INSERT INTO alerts (title, message, alert_type, is_read)
        VALUES ('Consumption Model Recalibrated', ?, 'info', 0)
        ''', (f"Updated 5-step parameters. New burn rate: {burn_rate:.3f} kg/d, estimated remaining: ~{days_rem} days.",))

        conn.commit()
        conn.close()
        return jsonify({
            "status": "success",
            "message": "Details saved and ML prediction recalibrated!",
            "new_burn_rate": burn_rate,
            "burn_rate_kg": burn_rate,
            "days_remaining": days_rem,
            "estimated_days_remaining": days_rem
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "failed", "error": f"Failed to save details: {str(e)}"}), 500

# ----------------- AUTHENTICATION & LOGIN APIs -----------------
@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    try:
        data = request.json or {}
        identifier = str(data.get("identifier", "")).strip()
        password = str(data.get("password", "")).strip()

        if not identifier or not password:
            return jsonify({"status": "failed", "error": "Consumer Number / Email and Password are required."}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? OR consumer_number = ?", (identifier, identifier))
        user_row = cursor.fetchone()

        if not user_row:
            cursor.execute("SELECT * FROM user_profile WHERE consumer_number = ? OR email = ?", (identifier, identifier))
            prof = cursor.fetchone()
            if prof and (password == "smartlpg123" or password == "admin"):
                user_dict = {
                    "id": prof["id"],
                    "full_name": prof["primary_name"],
                    "email": prof["email"],
                    "phone": prof["phone"],
                    "consumer_number": prof["consumer_number"],
                    "lpg_provider": prof["lpg_provider"]
                }
                conn.close()
                return jsonify({"status": "success", "message": "Login successful!", "user": user_dict})
            conn.close()
            return jsonify({"status": "failed", "error": "Invalid Consumer Number or Password. Use IND-7492810 / smartlpg123"}), 401

        user = dict(user_row)
        if user["password"] != password and password != "smartlpg123":
            conn.close()
            return jsonify({"status": "failed", "error": "Incorrect password. Default demo password is smartlpg123"}), 401

        user_dict = {
            "id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "phone": user.get("phone", ""),
            "consumer_number": user["consumer_number"],
            "lpg_provider": user.get("lpg_provider", "Indane Gas (IOCL)")
        }
        conn.close()
        return jsonify({"status": "success", "message": f"Welcome back, {user['full_name']}!", "user": user_dict})
    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)}), 500

@app.route("/api/auth/register", methods=["POST"])
def auth_register():
    try:
        data = request.json or {}
        full_name = str(data.get("full_name", "")).strip()
        email = str(data.get("email", "")).strip()
        phone = str(data.get("phone", "+91 98765 00000")).strip()
        provider = str(data.get("provider", "Indane Gas (IOCL)")).strip()
        password = str(data.get("password", "")).strip()

        if not full_name or not email or not password:
            return jsonify({"status": "failed", "error": "Full name, email, and password are required."}), 400

        prefix = "IND" if "Indane" in provider else ("BPCL" if "Bharat" in provider else "HPCL")
        consumer_no = data.get("consumer_number") or f"{prefix}-{random.randint(1000000, 9999999)}"

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({"status": "failed", "error": f"An account with email {email} already exists."}), 400

        cursor.execute('''
        INSERT INTO users (full_name, email, phone, consumer_number, password, lpg_provider)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (full_name, email, phone, consumer_no, password, provider))

        cursor.execute('''
        UPDATE user_profile SET
            primary_name = ?, phone = ?, email = ?, consumer_number = ?, lpg_provider = ?
        WHERE id = (SELECT id FROM user_profile ORDER BY id ASC LIMIT 1)
        ''', (full_name, phone, email, consumer_no, provider))

        conn.commit()
        conn.close()

        user_dict = {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "consumer_number": consumer_no,
            "lpg_provider": provider
        }
        return jsonify({"status": "success", "message": "Account created successfully!", "user": user_dict})
    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)}), 500

@app.route("/api/auth/current", methods=["GET"])
def auth_current():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_profile ORDER BY id ASC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            u = dict(row)
            return jsonify({
                "authenticated": True,
                "user": {
                    "full_name": u["primary_name"],
                    "email": u["email"],
                    "phone": u["phone"],
                    "consumer_number": u["consumer_number"],
                    "lpg_provider": u["lpg_provider"],
                    "distributor_name": u["distributor_name"]
                }
            })
        return jsonify({"authenticated": False, "user": None})
    except Exception as e:
        return jsonify({"authenticated": False, "error": str(e)})

@app.route("/api/family", methods=["GET"])
def get_family():
    return get_profile()

@app.route("/api/family", methods=["PUT"])
def update_family():
    return update_profile()

# ----------------- CYLINDER & PREDICTION APIs -----------------
@app.route("/api/cylinder/current", methods=["GET"])
def get_cylinder_status():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM user_profile LIMIT 1")
    user = cursor.fetchone()
    
    cursor.execute("SELECT * FROM cylinder_status ORDER BY id DESC LIMIT 1")
    cyl = cursor.fetchone()
    conn.close()
    
    if not cyl or not user:
        return jsonify({"error": "Data not initialized"}), 500
        
    lead_time = user["lead_time_days"]
    user_dict = dict(user)
    capacity = user_dict.get("cylinder_capacity", cyl["initial_gas_weight"])
    price = user_dict.get("current_refill_price", 858.00)
    analytics = compute_refill_analytics(
        current_gas_kg=cyl["current_gas_weight"],
        burn_rate_kg_per_day=cyl["burn_rate_kg_per_day"],
        lead_time_days=lead_time,
        cylinder_capacity=capacity,
        refill_price_inr=price
    )
    
    res = dict(cyl)
    res.update(analytics)
    res["tare_weight"] = cyl["tare_weight"]
    res["gross_weight"] = round(cyl["tare_weight"] + cyl["current_gas_weight"], 2)
    res["provider"] = user["lpg_provider"]
    res["consumer_number"] = user["consumer_number"]
    return jsonify(res)

@app.route("/api/predict/what-if", methods=["POST"])
def what_if_prediction():
    data = request.json or {}
    family_size = int(data.get("family_size", 4))
    meals_per_day = int(data.get("meals_per_day", 3))
    cooking_hours = float(data.get("cooking_hours", 2.5))
    diet_type = int(data.get("diet_type", 1))
    cylinder_capacity = float(data.get("cylinder_capacity", 14.2))
    flame_intensity = data.get("flame_intensity", "Medium")
    efficiency_mode = bool(data.get("efficiency_mode", False))
    refill_price = float(data.get("refill_price", 858.0))
    
    burn_rate = predict_consumption(
        family_size=family_size,
        meals_per_day=meals_per_day,
        daily_cooking_hours=cooking_hours,
        diet_type=diet_type,
        flame_intensity=flame_intensity,
        efficiency_mode=efficiency_mode
    )
    full_cycle_days = round(cylinder_capacity / burn_rate, 1) if burn_rate > 0 else 0
    cost_per_kg = refill_price / cylinder_capacity
    daily_cost = round(burn_rate * cost_per_kg, 2)
    monthly_cost = round(daily_cost * 30, 2)
    extra_days_saved = round(full_cycle_days * 0.176, 1) if not efficiency_mode else 0.0
    monthly_savings = round(monthly_cost * 0.15, 2) if not efficiency_mode else 0.0
    
    return jsonify({
        "family_size": family_size,
        "meals_per_day": meals_per_day,
        "cooking_hours": cooking_hours,
        "flame_intensity": flame_intensity,
        "efficiency_mode": efficiency_mode,
        "cylinder_capacity": cylinder_capacity,
        "predicted_burn_rate_kg": burn_rate,
        "estimated_cylinder_life_days": full_cycle_days,
        "monthly_cylinders_needed": round(30.0 / full_cycle_days, 2) if full_cycle_days > 0 else 1,
        "daily_cost_inr": daily_cost,
        "monthly_cost_inr": monthly_cost,
        "confidence_score": 97,
        "extra_days_saved": extra_days_saved,
        "monthly_savings_inr": monthly_savings
    })

# ----------------- REFILL HISTORY APIs -----------------
@app.route("/api/refills", methods=["GET"])
def get_refills():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM refill_history ORDER BY id DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    
    # Calculate summary metrics
    total_spent = sum(r["amount_paid"] for r in rows)
    avg_cycle = round(sum(r["days_lasted"] for r in rows) / len(rows), 1) if rows else 0
    avg_burn = round(sum(r["avg_daily_consumption"] for r in rows) / len(rows), 3) if rows else 0
    
    conn.close()
    return jsonify({
        "history": rows,
        "metrics": {
            "total_refills": len(rows),
            "total_spent_inr": round(total_spent, 2),
            "avg_cycle_days": avg_cycle,
            "avg_burn_rate_kg": avg_burn
        }
    })

# ----------------- ONE-CLICK BOOKING & TRACKING APIs -----------------
@app.route("/api/booking/create", methods=["POST"])
def create_booking():
    data = request.json or {}
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 25-Day Regulatory Lock Verification (MoPNG Inter-Booking Policy)
    force = bool(data.get("force", False))
    cursor.execute("SELECT * FROM bookings ORDER BY id DESC LIMIT 1")
    last_booking = cursor.fetchone()
    
    if last_booking and not force:
        # Check 1: Is previous order still active in transit?
        if last_booking["tracking_step"] < 5 and last_booking["status"] != "DELIVERED":
            conn.close()
            return jsonify({
                "status": "locked",
                "error": f"Active Refill In Progress: Booking #{last_booking['booking_id']} is currently out for delivery (Step {last_booking['tracking_step']}/5). You cannot book another refill until this one is delivered.",
                "booking_id": last_booking["booking_id"],
                "tracking_step": last_booking["tracking_step"]
            }), 400
            
        # Check 2: Has 25 days elapsed since last refill booking?
        try:
            last_date = datetime.strptime(last_booking["booking_date"], "%Y-%m-%d")
            days_elapsed = (datetime.now() - last_date).days
        except Exception:
            days_elapsed = 30
            
        if days_elapsed < 25:
            days_remaining = 25 - days_elapsed
            eligible_date = (last_date + timedelta(days=25)).strftime("%d %b %Y")
            conn.close()
            return jsonify({
                "status": "locked",
                "error": f"Refill Booking Locked: Regulatory guidelines require a minimum 25-day interval between cylinder bookings. Next booking allowed in {days_remaining} day(s) on {eligible_date}.",
                "days_elapsed": days_elapsed,
                "days_remaining": days_remaining,
                "eligible_date": eligible_date
            }), 400

    cursor.execute("SELECT * FROM user_profile LIMIT 1")
    user = cursor.fetchone()
    
    provider = data.get("provider", user["lpg_provider"] if user else "Indane Gas")
    consumer_no = data.get("consumer_number", user["consumer_number"] if user else "IND-7492810")
    cylinder_type = data.get("cylinder_type", "14.2 kg Domestic Refill")
    payment_mode = data.get("payment_mode", "UPI (Google Pay / PhonePe)")
    lead_time = user["lead_time_days"] if user else 3
    
    # Generate realistic reference ID
    prefix = "IND" if "Indane" in provider else ("BPCL" if "Bharat" in provider else "HPCL")
    booking_id = f"LPG-{prefix}-{datetime.now().year}-{random.randint(1000, 9999)}"
    
    booking_date = datetime.now().strftime("%Y-%m-%d")
    est_delivery = (datetime.now() + timedelta(days=lead_time)).strftime("%Y-%m-%d")
    otp = str(random.randint(1000, 9999))
    agents = [
        ("Suresh Naik", "+91 98450 11234"),
        ("Ramesh Kumar", "+91 94481 29401"),
        ("Vinod Sharma", "+91 97312 88450"),
        ("Mahesh Gowda", "+91 99001 77321")
    ]
    agent_name, agent_phone = random.choice(agents)
    amount = 858.00
    
    cursor.execute('''
    INSERT INTO bookings (
        booking_id, consumer_number, provider, cylinder_type,
        amount, payment_mode, booking_date, estimated_delivery_date,
        status, delivery_agent_name, delivery_agent_phone, delivery_otp, tracking_step
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'BOOKED', ?, ?, ?, 1)
    ''', (
        booking_id, consumer_no, provider, cylinder_type,
        amount, payment_mode, booking_date, est_delivery,
        agent_name, agent_phone, otp
    ))
    
    # Add an alert
    cursor.execute('''
    INSERT INTO alerts (title, message, alert_type, is_read)
    VALUES (?, ?, 'info', 0)
    ''', (
        f"LPG Booking Confirmed: {booking_id}",
        f"Refill cylinder booked successfully with {provider}. Expected delivery: {est_delivery}. Delivery OTP: {otp}."
    ))
    
    conn.commit()
    
    cursor.execute("SELECT * FROM bookings WHERE booking_id = ?", (booking_id,))
    new_booking = dict(cursor.fetchone())
    conn.close()
    
    return jsonify({
        "status": "success",
        "message": "Refill booked successfully!",
        "booking": new_booking
    })

@app.route("/api/booking/active", methods=["GET"])
def get_active_booking():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    if row:
        b = dict(row)
        try:
            last_date = datetime.strptime(b["booking_date"], "%Y-%m-%d")
            days_elapsed = (datetime.now() - last_date).days
        except Exception:
            days_elapsed = 30
            last_date = datetime.now() - timedelta(days=30)
            
        is_delivered = (b["tracking_step"] >= 5 or b["status"] == "DELIVERED")
        can_book = (days_elapsed >= 25) and is_delivered
        days_remaining = max(0, 25 - days_elapsed)
        eligible_date = (last_date + timedelta(days=25)).strftime("%d %b %Y")
        
        lock_reason = None
        if not is_delivered:
            lock_reason = f"Booking #{b['booking_id']} is active and en route (Step {b['tracking_step']}/5)."
        elif days_elapsed < 25:
            lock_reason = f"Regulatory 25-day inter-booking interval active. Next eligible booking: {eligible_date} ({days_remaining} days left)."
            
        b["eligibility"] = {
            "can_book": can_book,
            "days_elapsed": days_elapsed,
            "days_remaining": days_remaining,
            "eligible_date": eligible_date,
            "is_delivered": is_delivered,
            "lock_reason": lock_reason
        }
        return jsonify(b)
        
    return jsonify({
        "active_booking": None,
        "eligibility": {
            "can_book": True,
            "days_elapsed": 30,
            "days_remaining": 0,
            "eligible_date": datetime.now().strftime("%d %b %Y"),
            "lock_reason": None
        }
    })

@app.route("/api/booking/fast-forward-25-days", methods=["POST"])
def fast_forward_booking_demo():
    conn = get_db_connection()
    cursor = conn.cursor()
    past_date = (datetime.now() - timedelta(days=26)).strftime("%Y-%m-%d")
    cursor.execute('''
    UPDATE bookings 
    SET booking_date = ?, tracking_step = 5, status = 'DELIVERED'
    WHERE id = (SELECT id FROM bookings ORDER BY id DESC LIMIT 1)
    ''', (past_date,))
    conn.commit()
    conn.close()
    return jsonify({
        "success": True,
        "message": "Demo: Simulated 26 days passed since last refill. 25-day lock is now lifted!"
    })

@app.route("/api/booking/advance-step/<booking_id>", methods=["POST"])
def advance_tracking_step(booking_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings WHERE booking_id = ?", (booking_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return jsonify({"error": "Booking not found"}), 404
        
    steps = [
        (1, "BOOKED"),
        (2, "CONFIRMED"),
        (3, "DISPATCHED"),
        (4, "OUT_FOR_DELIVERY"),
        (5, "DELIVERED")
    ]
    current_step = row["tracking_step"]
    
    # If already delivered (step 5), cycle back to Step 1 for repeatable evaluation demo
    if current_step >= 5:
        next_step = 1
        new_status = "BOOKED"
        new_otp = str(random.randint(1000, 9999))
        est_delivery = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        cursor.execute('''
        UPDATE bookings SET tracking_step = 1, status = 'BOOKED', delivery_otp = ?, estimated_delivery_date = ?
        WHERE booking_id = ?
        ''', (new_otp, est_delivery, booking_id))
        
        # Reset cylinder back to low gas level to show depleted state
        cursor.execute('''
        UPDATE cylinder_status 
        SET current_gas_weight = 2.45, days_remaining = 5.8, is_leak_detected = 0, status = 'Active - Low Gas (17.3%)'
        WHERE id = (SELECT id FROM cylinder_status ORDER BY id DESC LIMIT 1)
        ''')
        
        cursor.execute('''
        INSERT INTO alerts (title, message, alert_type, is_read)
        VALUES ('Demo Tracking Restarted', 'Refill workflow reset to Step 1 (Order Booked). Gas reserve level: 2.45 kg.', 'info', 0)
        ''')
        conn.commit()
        conn.close()
        return jsonify({"booking_id": booking_id, "step": 1, "status": "BOOKED", "reset": True})

    next_step = min(5, current_step + 1)
    new_status = steps[next_step - 1][1]
    
    cursor.execute('''
    UPDATE bookings SET tracking_step = ?, status = ? WHERE booking_id = ?
    ''', (next_step, new_status, booking_id))
    
    # If delivered, record in refill history and replenish active cylinder
    if new_status == "DELIVERED":
        cursor.execute('''
        INSERT OR IGNORE INTO refill_history (
            booking_id, booking_date, delivery_date, provider, cylinder_capacity,
            amount_paid, days_lasted, avg_daily_consumption, payment_mode, status
        ) VALUES (?, ?, ?, ?, 14.2, ?, 34, 0.42, ?, 'Delivered')
        ''', (
            booking_id, row["booking_date"], datetime.now().strftime("%Y-%m-%d"),
            row["provider"], row["amount"], row["payment_mode"]
        ))
        
        # Replenish active cylinder directly on current connection (avoids SQLite lock contention)
        burn_rate = 0.42
        days_rem = round(14.2 / burn_rate, 1)
        serial = f"CYL-IND-{random.randint(1000, 9999)}X"
        now_str = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute('''
        INSERT INTO cylinder_status (
            cylinder_serial, installed_date, tare_weight, initial_gas_weight,
            current_gas_weight, burn_rate_kg_per_day, days_remaining,
            status, is_leak_detected, iot_sync_enabled
        ) VALUES (?, ?, 15.3, 14.2, 14.2, ?, ?, 'Active - 100% Full', 0, 1)
        ''', (serial, now_str, burn_rate, days_rem))
        
        cursor.execute('''
        INSERT INTO alerts (title, message, alert_type, is_read)
        VALUES ('LPG Refill Delivered!', 'Your cylinder has been delivered and mounted successfully (14.2 kg available).', 'success', 0)
        ''')

    conn.commit()
    conn.close()
    
    return jsonify({"booking_id": booking_id, "step": next_step, "status": new_status})

@app.route("/api/booking/reset-demo", methods=["POST"])
def reset_tracking_demo():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT booking_id FROM bookings ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    
    new_otp = str(random.randint(1000, 9999))
    est_delivery = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    
    if row:
        booking_id = row["booking_id"]
        cursor.execute('''
        UPDATE bookings 
        SET tracking_step = 1, status = 'BOOKED', delivery_otp = ?, estimated_delivery_date = ?
        WHERE booking_id = ?
        ''', (new_otp, est_delivery, booking_id))
    else:
        booking_id = f"LPG-IND-2026-{random.randint(1000, 9999)}"
        cursor.execute('''
        INSERT INTO bookings (
            booking_id, consumer_number, provider, cylinder_type,
            booking_date, estimated_delivery_date, delivery_agent_name,
            delivery_agent_phone, delivery_otp, tracking_step, status,
            amount, payment_mode
        ) VALUES (?, 'IND-7492810', 'Indane Gas Services', '14.2 kg Domestic Refill',
            ?, ?, 'Ramesh Kumar', '+91 94481 29401', ?, 1, 'BOOKED', 858.00, 'UPI (Google Pay / PhonePe)')
        ''', (booking_id, datetime.now().strftime("%Y-%m-%d"), est_delivery, new_otp))
        
    # Set cylinder back to low gas (2.45 kg) to demonstrate depletion warning and alerts
    cursor.execute('''
    UPDATE cylinder_status 
    SET current_gas_weight = 2.45, days_remaining = 5.8, is_leak_detected = 0, status = 'Active - Low Gas (17.3%)'
    WHERE id = (SELECT id FROM cylinder_status ORDER BY id DESC LIMIT 1)
    ''')
    
    cursor.execute('''
    INSERT INTO alerts (title, message, alert_type, is_read)
    VALUES ('Demo Reset', 'Tracking demo reset to Step 1 (Order Booked). Reserve fuel level set to 2.45 kg.', 'info', 0)
    ''')
    
    conn.commit()
    conn.close()
    return jsonify({"success": True, "booking_id": booking_id, "step": 1, "status": "BOOKED", "otp": new_otp})

# ----------------- ALERTS & NOTIFICATIONS APIs -----------------
@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT 10")
    alerts = [dict(r) for r in cursor.fetchall()]
    cursor.execute("SELECT COUNT(*) FROM alerts WHERE is_read = 0")
    unread_count = cursor.fetchone()[0]
    conn.close()
    return jsonify({"alerts": alerts, "unread_count": unread_count})

@app.route("/api/alerts/mark-all-read", methods=["POST"])
def mark_alerts_read():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE alerts SET is_read = 1")
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

# ----------------- IOT TELEMETRY & SIMULATOR APIs -----------------
@app.route("/api/iot/telemetry", methods=["GET"])
def get_iot_telemetry():
    telemetry = IoTSimulator.get_current_telemetry()
    return jsonify(telemetry)

@app.route("/api/iot/simulate-cooking", methods=["POST"])
def simulate_cooking():
    data = request.json or {}
    hours = float(data.get("hours", 1.0))
    intensity = data.get("intensity", "Medium")
    result = IoTSimulator.simulate_cooking(hours, intensity)
    return jsonify(result)

@app.route("/api/iot/simulate-leak", methods=["POST"])
def simulate_leak():
    data = request.json or {}
    active = bool(data.get("active", True))
    result = IoTSimulator.trigger_leak_simulation(active)
    return jsonify(result)

@app.route("/api/iot/reset-cylinder", methods=["POST"])
def reset_cylinder():
    result = IoTSimulator.install_new_cylinder(14.2, 15.3)
    return jsonify(result)

if __name__ == "__main__":
    print("Starting SmartLPG Flask Server on http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=True)
