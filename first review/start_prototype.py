import sys
import os

curr_dir = os.path.dirname(os.path.abspath(__file__))
prototype_dir = os.path.join(curr_dir, "prototype")
sys.path.insert(0, prototype_dir)

from app import app

if __name__ == "__main__":
    print("=" * 65)
    print("SmartLPG Review 1 Prototype (40% Implementation Scope Functional)")
    print("Running at: http://127.0.0.1:5001")
    print("=" * 65)
    app.run(host="127.0.0.1", port=5001, debug=False)
