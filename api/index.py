import os
import sys

# Ensure root directory is on sys.path so 'backend' can be imported
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.database import init_db
from backend.app import app

# Ensure SQLite database is initialized in /tmp if running in serverless environment
init_db()

# Vercel looks for the WSGI application instance named `app`
