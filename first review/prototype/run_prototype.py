import sys
import os

# Set base path
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_dir)

from app import app

if __name__ == "__main__":
    print("=" * 65)
    print("Starting SmartLPG Mini Project Review 1 Prototype Server (Port 5001)")
    print("Implementation Scope: 40% Functional (Sensor-Free ML Prediction)")
    print("URL: http://127.0.0.1:5001")
    print("=" * 65)
    app.run(host="127.0.0.1", port=5001, debug=False)
