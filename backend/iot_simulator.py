import os
import random
from datetime import datetime
from backend.database import get_db_connection

class IoTSimulator:
    """
    Simulates HX711 Load Cell Weight Sensor and Gas Telemetry Node (ESP32/Arduino).
    Tracks Tare Weight, Net Gas, Gross Weight, Battery Level, and Anomaly/Leak Detection.
    """
    
    @staticmethod
    def get_current_telemetry():
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM cylinder_status ORDER BY id DESC LIMIT 1")
        cyl = cursor.fetchone()
        
        cursor.execute("SELECT * FROM iot_telemetry ORDER BY id DESC LIMIT 1")
        last_iot = cursor.fetchone()
        
        conn.close()
        
        if not cyl:
            return None
            
        tare_weight = cyl["tare_weight"]
        net_lpg = cyl["current_gas_weight"]
        # Add slight realistic load-cell sensor jitter (+- 0.02 kg)
        jitter = round(random.uniform(-0.015, 0.015), 3)
        gross_weight = round(tare_weight + net_lpg + jitter, 2)
        
        return {
            "sensor_id": "HX711-ESP32-NODE-1",
            "gross_weight": gross_weight,
            "tare_weight": tare_weight,
            "net_lpg_weight": round(net_lpg, 2),
            "initial_gas_weight": cyl["initial_gas_weight"],
            "battery_level": last_iot["battery_level"] if last_iot else 94,
            "leak_detected": bool(cyl["is_leak_detected"]),
            "status": cyl["status"],
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    @staticmethod
    def simulate_cooking(hours_cooked=1.0, burner_intensity="Medium"):
        """
        Simulates gas consumption during a cooking session.
        Standard burner consumes ~0.15 to 0.25 kg/hour.
        """
        multiplier = {"Low": 0.12, "Medium": 0.18, "High": 0.28}.get(burner_intensity, 0.18)
        gas_used = round(hours_cooked * multiplier, 3)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM cylinder_status ORDER BY id DESC LIMIT 1")
        cyl = cursor.fetchone()
        
        if not cyl:
            conn.close()
            return {"error": "No active cylinder"}
            
        new_gas = max(0.0, round(cyl["current_gas_weight"] - gas_used, 3))
        burn_rate = cyl["burn_rate_kg_per_day"]
        days_rem = round(new_gas / burn_rate, 1) if burn_rate > 0 else 0
        
        cursor.execute('''
        UPDATE cylinder_status 
        SET current_gas_weight = ?, days_remaining = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (new_gas, days_rem, cyl["id"]))
        
        # Log to telemetry
        gross = round(cyl["tare_weight"] + new_gas, 2)
        cursor.execute('''
        INSERT INTO iot_telemetry (sensor_id, gross_weight, tare_weight, net_lpg_weight, battery_level, leak_detected)
        VALUES ('HX711-ESP32-NODE-1', ?, ?, ?, 93, 0)
        ''', (gross, cyl["tare_weight"], new_gas))
        
        conn.commit()
        conn.close()
        
        return {
            "gas_used_kg": gas_used,
            "remaining_gas_kg": new_gas,
            "days_remaining": days_rem,
            "message": f"Simulated {hours_cooked}h {burner_intensity} cooking session. Consumed {gas_used} kg LPG."
        }

    @staticmethod
    def trigger_leak_simulation(active=True):
        """
        Simulates an anomalous rapid weight drop indicating a gas leak.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM cylinder_status ORDER BY id DESC LIMIT 1")
        cyl = cursor.fetchone()
        
        if not cyl:
            conn.close()
            return {"error": "No active cylinder"}
            
        new_status = "CRITICAL: Gas Leak Anomaly Detected!" if active else "Active"
        cursor.execute('''
        UPDATE cylinder_status 
        SET is_leak_detected = ?, status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (1 if active else 0, new_status, cyl["id"]))
        
        if active:
            cursor.execute('''
            INSERT INTO alerts (title, message, alert_type, is_read)
            VALUES (
                'EMERGENCY: Gas Leak Detected!',
                'Safety anomaly detector algorithm identified abnormal gas depletion (-0.48 kg in 10 mins). Turn off cylinder regulator immediately and ventilate kitchen area!',
                'critical', 0
            )
            ''')
            
        conn.commit()
        conn.close()
        return {"leak_active": active, "message": "Gas leak alert triggered!" if active else "Leak status resolved."}

    @staticmethod
    def install_new_cylinder(cylinder_capacity=14.2, tare_weight=15.3):
        """
        Simulates mounting a brand new sealed cylinder onto the load cell.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        burn_rate = 0.42
        days_rem = round(cylinder_capacity / burn_rate, 1)
        serial = f"CYL-IND-{random.randint(1000, 9999)}X"
        now_str = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute('''
        INSERT INTO cylinder_status (
            cylinder_serial, installed_date, tare_weight, initial_gas_weight,
            current_gas_weight, burn_rate_kg_per_day, days_remaining,
            status, is_leak_detected, iot_sync_enabled
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 'Active - 100% Full', 0, 1)
        ''', (serial, now_str, tare_weight, cylinder_capacity, cylinder_capacity, burn_rate, days_rem))
        
        gross = round(tare_weight + cylinder_capacity, 2)
        cursor.execute('''
        INSERT INTO iot_telemetry (sensor_id, gross_weight, tare_weight, net_lpg_weight, battery_level, leak_detected)
        VALUES ('DATA-STREAM-NODE-1', ?, ?, ?, 99, 0)
        ''', (gross, tare_weight, cylinder_capacity))
        
        cursor.execute('''
        INSERT INTO alerts (title, message, alert_type, is_read)
        VALUES ('New Cylinder Mounted', 'New cylinder {0} installed and verified. 100% capacity ({1} kg).', 'success', 0)
        '''.format(serial, cylinder_capacity))
        
        conn.commit()
        conn.close()
        return {"status": "success", "serial": serial, "net_gas": cylinder_capacity}
