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
from backend.ml_model import predict_consumption, compute_refill_analytics
from backend.iot_simulator import IoTSimulator

# Base directories
TEMPLATE_DIR = os.path.join(BASE_DIR, "frontend", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
CORS(app)

# Ensure DB is initialized
init_db()

# ----------------- WEB PAGES -----------------
@app.route("/")
@app.route("/api")
@app.route("/api/index")
def index():
    return render_template("index.html")

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
            "current_refill_price": 858.00
        }
        for k, v in defaults.items():
            if k not in data or data[k] is None:
                data[k] = v
        return jsonify(data)
    return jsonify({"error": "Profile not found"}), 404

@app.route("/api/profile", methods=["PUT"])
def update_profile():
    data = request.json or {}
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM user_profile ORDER BY id ASC LIMIT 1")
    user = cursor.fetchone()
    if not user:
        conn.close()
        return jsonify({"error": "Profile not found"}), 404

    cursor.execute("PRAGMA table_info(user_profile)")
    rows = cursor.fetchall()
    existing_cols = {row["name"] if hasattr(row, "keys") else row[1] for row in rows}

    allowed_fields = [
        "primary_name", "phone", "email", "address", "lpg_provider", "consumer_number",
        "distributor_name", "distributor_phone", "connection_type",
        "family_size", "adults_count", "children_count", "cooking_meals_per_day",
        "daily_cooking_hours", "usage_purpose", "household_classification",
        "cylinder_capacity", "date_of_last_refill", "current_refill_price", "lead_time_days"
    ]
    
    update_fields = {}
    for field in allowed_fields:
        if field in data and field in existing_cols:
            val = data[field]
            if field in ["family_size", "adults_count", "children_count", "cooking_meals_per_day", "lead_time_days"]:
                val = int(val)
            elif field in ["daily_cooking_hours", "cylinder_capacity", "current_refill_price"]:
                val = float(val)
            update_fields[field] = val

    if update_fields:
        set_clause = ", ".join([f"{k} = ?" for k in update_fields.keys()])
        params = list(update_fields.values()) + [user["id"]]
        cursor.execute(f"UPDATE user_profile SET {set_clause} WHERE id = ?", params)
    
    # Recalculate burn rate with updated profile
    f_size = int(data.get("family_size", user["family_size"]))
    meals = int(data.get("cooking_meals_per_day", user["cooking_meals_per_day"]))
    hours = float(data.get("daily_cooking_hours", user["daily_cooking_hours"]))

    burn_rate = predict_consumption(
        family_size=f_size,
        meals_per_day=meals,
        daily_cooking_hours=hours
    )
    
    # Update active cylinder burn rate and days remaining
    cursor.execute("SELECT * FROM cylinder_status ORDER BY id DESC LIMIT 1")
    cyl = cursor.fetchone()
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

    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Profile updated successfully", "new_burn_rate": burn_rate})
    cyl = cursor.fetchone()
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

    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Profile updated successfully", "new_burn_rate": burn_rate})

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
        return jsonify(dict(row))
    return jsonify({"active_booking": None})

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
        
        # Reset cylinder to 14.2 kg
        IoTSimulator.install_new_cylinder(14.2, 15.3)
        
        cursor.execute('''
        INSERT INTO alerts (title, message, alert_type, is_read)
        VALUES ('LPG Refill Delivered!', 'Your cylinder has been delivered and mounted. Load cell reset to 100% (14.2 kg).', 'success', 0)
        ''')

    conn.commit()
    conn.close()
    
    return jsonify({"booking_id": booking_id, "step": next_step, "status": new_status})

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
