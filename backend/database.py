import sqlite3
import os
import shutil
from datetime import datetime, timedelta

DB_DIR = os.path.dirname(__file__)
SOURCE_DB = os.path.join(DB_DIR, "smart_lpg.db")

def get_db_path():
    # In serverless environments like Vercel, the app root is read-only.
    # We copy the database to /tmp to allow SQLite read/write operations.
    if os.environ.get("VERCEL"):
        db_path = "/tmp/smart_lpg.db"
        if not os.path.exists(db_path) and os.path.exists(SOURCE_DB):
            try:
                shutil.copy2(SOURCE_DB, db_path)
            except Exception:
                pass
        return db_path
    return SOURCE_DB

def get_db_connection():
    conn = sqlite3.connect(get_db_path(), timeout=30.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # User Profile Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_profile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        primary_name TEXT NOT NULL,
        secondary_name TEXT,
        usn_primary TEXT,
        usn_secondary TEXT,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        address TEXT NOT NULL,
        lpg_provider TEXT NOT NULL,
        consumer_number TEXT NOT NULL,
        distributor_name TEXT NOT NULL,
        distributor_phone TEXT DEFAULT '+91 80 2520 1199',
        connection_type TEXT DEFAULT '14.2 kg Subsidized Domestic',
        family_size INTEGER NOT NULL,
        adults_count INTEGER DEFAULT 2,
        children_count INTEGER DEFAULT 2,
        cooking_meals_per_day INTEGER NOT NULL,
        daily_cooking_hours REAL NOT NULL,
        usage_purpose TEXT DEFAULT 'Household',
        household_classification TEXT DEFAULT 'Family Household',
        cylinder_capacity REAL NOT NULL,
        date_of_last_refill TEXT DEFAULT '2026-10-12',
        current_refill_price REAL DEFAULT 858.00,
        lead_time_days INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Current Cylinder Status Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cylinder_status (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cylinder_serial TEXT NOT NULL,
        installed_date TEXT NOT NULL,
        tare_weight REAL NOT NULL,
        initial_gas_weight REAL NOT NULL,
        current_gas_weight REAL NOT NULL,
        burn_rate_kg_per_day REAL NOT NULL,
        predicted_empty_date TEXT,
        days_remaining REAL,
        status TEXT NOT NULL,
        is_leak_detected INTEGER DEFAULT 0,
        iot_sync_enabled INTEGER DEFAULT 1,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Refill History Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS refill_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id TEXT UNIQUE NOT NULL,
        booking_date TEXT NOT NULL,
        delivery_date TEXT NOT NULL,
        provider TEXT NOT NULL,
        cylinder_capacity REAL NOT NULL,
        amount_paid REAL NOT NULL,
        days_lasted INTEGER NOT NULL,
        avg_daily_consumption REAL NOT NULL,
        payment_mode TEXT NOT NULL,
        status TEXT NOT NULL
    )
    ''')

    # Active and Past Bookings Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id TEXT UNIQUE NOT NULL,
        consumer_number TEXT NOT NULL,
        provider TEXT NOT NULL,
        cylinder_type TEXT NOT NULL,
        amount REAL NOT NULL,
        payment_mode TEXT NOT NULL,
        booking_date TEXT NOT NULL,
        estimated_delivery_date TEXT NOT NULL,
        status TEXT NOT NULL, -- BOOKED, CONFIRMED, DISPATCHED, OUT_FOR_DELIVERY, DELIVERED
        delivery_agent_name TEXT,
        delivery_agent_phone TEXT,
        delivery_otp TEXT,
        tracking_step INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Alerts & Notifications Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        alert_type TEXT NOT NULL, -- warning, critical, info, success
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # IoT Sensor Telemetry Logs Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS iot_telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sensor_id TEXT NOT NULL,
        gross_weight REAL NOT NULL,
        tare_weight REAL NOT NULL,
        net_lpg_weight REAL NOT NULL,
        battery_level INTEGER NOT NULL,
        leak_detected INTEGER DEFAULT 0,
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    migrate_db(conn)
    seed_initial_data(conn)
    conn.close()

def migrate_db(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(user_profile)")
        rows = cursor.fetchall()
        existing_cols = [row["name"] if hasattr(row, "keys") else row[1] for row in rows]

        new_cols = [
            ("distributor_phone", "TEXT DEFAULT '+91 80 2520 1199'"),
            ("connection_type", "TEXT DEFAULT '14.2 kg Subsidized Domestic'"),
            ("adults_count", "INTEGER DEFAULT 2"),
            ("children_count", "INTEGER DEFAULT 2"),
            ("usage_purpose", "TEXT DEFAULT 'Household'"),
            ("household_classification", "TEXT DEFAULT 'Family Household'"),
            ("date_of_last_refill", "TEXT DEFAULT '2026-10-12'"),
            ("current_refill_price", "REAL DEFAULT 858.00")
        ]
        for col_name, col_type in new_cols:
            if col_name not in existing_cols:
                try:
                    cursor.execute(f"ALTER TABLE user_profile ADD COLUMN {col_name} {col_type}")
                except Exception:
                    pass

        conn.commit()
    except Exception as e:
        print(f"Migration note: {e}")

def seed_initial_data(conn):
    cursor = conn.cursor()

    # Check if profile exists
    cursor.execute("SELECT COUNT(*) FROM user_profile")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO user_profile (
            primary_name, secondary_name, usn_primary, usn_secondary, phone, email,
            address, lpg_provider, consumer_number, distributor_name, distributor_phone, connection_type,
            family_size, adults_count, children_count, cooking_meals_per_day, daily_cooking_hours,
            usage_purpose, household_classification, cylinder_capacity, date_of_last_refill, current_refill_price, lead_time_days
        ) VALUES (
            'Mohammed Huzaifa Khan', 'Mohammad Aftab Ahmed', '1NH24CS126', '1NH24CS125',
            '+91 98765 43210', 'huzaifa.aftab.smartlpg@gmail.com',
            'Flat 402, Greenview Heights, Indiranagar, Bengaluru, KA 560038',
            'Indane Gas (IOCL)', 'IND-7492810', 'Shanthi Indane Gas Services', '+91 80 2520 1199', '14.2 kg Subsidized Domestic',
            4, 2, 2, 3, 2.8,
            'Household', 'Family Household', 14.2, '2026-10-12', 858.00, 3
        )
        ''')

    # Seed Refill History (Past 6 refills)
    cursor.execute("SELECT COUNT(*) FROM refill_history")
    if cursor.fetchone()[0] == 0:
        past_refills = [
            ("LPG-IND-2026-0104", "2026-01-02", "2026-01-05", "Indane", 14.2, 852.00, 36, 0.394, "UPI / GPay", "Delivered"),
            ("LPG-IND-2026-0218", "2026-02-08", "2026-02-11", "Indane", 14.2, 852.00, 34, 0.417, "Net Banking", "Delivered"),
            ("LPG-IND-2026-0322", "2026-03-15", "2026-03-18", "Indane", 14.2, 856.50, 33, 0.430, "UPI / PhonePe", "Delivered"),
            ("LPG-IND-2026-0428", "2026-04-19", "2026-04-22", "Indane", 14.2, 856.50, 35, 0.405, "Cash on Delivery", "Delivered"),
            ("LPG-IND-2026-0601", "2026-05-26", "2026-05-29", "Indane", 14.2, 858.00, 32, 0.443, "UPI / GPay", "Delivered"),
            ("LPG-IND-2026-0710", "2026-07-01", "2026-07-04", "Indane", 14.2, 858.00, 34, 0.418, "Credit Card", "Delivered"),
        ]
        cursor.executemany('''
        INSERT INTO refill_history (
            booking_id, booking_date, delivery_date, provider, cylinder_capacity,
            amount_paid, days_lasted, avg_daily_consumption, payment_mode, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', past_refills)

    # Seed Cylinder Status (Currently ~2.45 kg gas remaining -> ~5.8 days left, low gas alert)
    cursor.execute("SELECT COUNT(*) FROM cylinder_status")
    if cursor.fetchone()[0] == 0:
        installed_date = (datetime.now() - timedelta(days=28)).strftime("%Y-%m-%d")
        burn_rate = 0.42
        current_gas = 2.45
        days_rem = round(current_gas / burn_rate, 1)
        pred_empty = (datetime.now() + timedelta(days=days_rem)).strftime("%Y-%m-%d")

        cursor.execute('''
        INSERT INTO cylinder_status (
            cylinder_serial, installed_date, tare_weight, initial_gas_weight,
            current_gas_weight, burn_rate_kg_per_day, predicted_empty_date,
            days_remaining, status, is_leak_detected, iot_sync_enabled
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            "CYL-IND-9942B", installed_date, 15.3, 14.2, current_gas,
            burn_rate, pred_empty, days_rem, "Active - Low Gas Alert", 0, 1
        ))

    # Seed an active booking in progress for demonstration
    cursor.execute("SELECT COUNT(*) FROM bookings")
    if cursor.fetchone()[0] == 0:
        today_str = datetime.now().strftime("%Y-%m-%d")
        est_deliv = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        cursor.execute('''
        INSERT INTO bookings (
            booking_id, consumer_number, provider, cylinder_type,
            amount, payment_mode, booking_date, estimated_delivery_date,
            status, delivery_agent_name, delivery_agent_phone, delivery_otp, tracking_step
        ) VALUES (
            'LPG-IND-2026-9402', 'IND-7492810', 'Indane Gas (IOCL)', '14.2 kg Domestic Refill',
            858.00, 'UPI (Google Pay)', ?, ?, 'DISPATCHED', 'Ramesh Kumar', '+91 94481 29401', '4912', 3
        )
        ''', (today_str, est_deliv))

    # Seed Alerts
    cursor.execute("SELECT COUNT(*) FROM alerts")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO alerts (title, message, alert_type, is_read)
        VALUES 
        ('Refill Recommended', 'Current LPG reserve is at 2.45 kg (approx. 5.8 days). Factoring in 3-day delivery lead time, booking now avoids outages.', 'warning', 0),
        ('Refill Order Dispatched', 'Booking LPG-IND-2026-9402 has been dispatched from Shanthi Indane Agency. Delivery Agent: Ramesh Kumar (+91 94481 29401). OTP: 4912.', 'info', 0),
        ('Real-Time Data Stream Active', 'Data analytics pipeline connected. Current gross weight: 17.75 kg (Tare: 15.30 kg, Net Gas: 2.45 kg). No gas leaks detected.', 'success', 0)
        ''')

    # Seed recent telemetry
    cursor.execute("SELECT COUNT(*) FROM iot_telemetry")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO iot_telemetry (sensor_id, gross_weight, tare_weight, net_lpg_weight, battery_level, leak_detected)
        VALUES ('DATA-STREAM-NODE-1', 17.75, 15.30, 2.45, 94, 0)
        ''')

    conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)
