import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from ml_engine import engine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.json or {}
    cylinder_capacity = float(data.get("cylinder_capacity", 14.2))
    refill_date = data.get("refill_date", None)
    family_size = int(data.get("family_size", 4))
    meals_per_day = int(data.get("meals_per_day", 3))
    cooking_hours = float(data.get("cooking_hours", 2.8))
    lead_time_days = int(data.get("lead_time_days", 3))
    flame_intensity = data.get("flame_intensity", "Medium")

    result = engine.compute_timeline(
        cylinder_capacity=cylinder_capacity,
        refill_date_str=refill_date,
        family_size=family_size,
        meals_per_day=meals_per_day,
        cooking_hours=cooking_hours,
        lead_time_days=lead_time_days,
        flame_intensity=flame_intensity
    )
    return jsonify(result)

@app.route("/api/review-milestone", methods=["GET"])
def get_milestone_info():
    return jsonify({
        "review": "Review 1 (CIE Evaluation)",
        "course": "24CSE57 - Societal Based Mini Project",
        "semester": "V",
        "department": "Computer Science & Engineering",
        "students": [
            {"name": "Mohammed Huzaifa Khan", "usn": "1NH24CS126"},
            {"name": "Mohammad Aftab Ahmed", "usn": "1NH24CS125"}
        ],
        "guide": "Prof. Ashwini G B",
        "implementation_completion": "40%",
        "completed_modules_review1": [
            "Household Demographics & Cooking Pattern Profiling",
            "Synthetic Domestic Energy Dataset & Feature Extraction (N=600)",
            "Random Forest ML Consumption Forecasting (R² ≈ 0.9634)",
            "Remaining Gas & Days-to-Empty Mathematical Estimation",
            "Buffer-Aware Refill Advisory Warning Alert Engine"
        ],
        "planned_modules_review2": [
            "One-Click Booking API Integration with OMC Distributors (Indane/BPCL/HPCL)",
            "5-Stage Live Delivery Lifecycle Stepper with Doorstep OTP Verification",
            "Cellular SMS / WhatsApp Gateway Notification Dispatcher",
            "Advanced Multi-Factor Energy Advisor & Printable PDF Audit Report",
            "Final Bound Thesis Report & Plagiarism Certification"
        ]
    })

if __name__ == "__main__":
    print("=" * 65)
    print("SmartLPG - Review 1 Functional Prototype Server (40% Scope)")
    print("Running on: http://127.0.0.1:5001")
    print("=" * 65)
    app.run(host="127.0.0.1", port=5001, debug=False)
