import os
import sys

# Ensure Smart_LPG root directory is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from backend.database import init_db
from backend.app import app

if __name__ == "__main__":
    init_db()
    print("=" * 65)
    print("SmartLPG: Intelligent LPG Refill Prediction & Booking System")
    print("Course: Societal Based Mini Project (24CSE57) - Semester V")
    print("Students: Mohammed Huzaifa Khan (1NH24CS126) & Mohammad Aftab Ahmed (1NH24CS125)")
    print("Guide: Prof. Ashwini G B - Department of CSE")
    print("Server running on: http://127.0.0.1:5000")
    print("=" * 65)
    app.run(host="127.0.0.1", port=5000, debug=False)
