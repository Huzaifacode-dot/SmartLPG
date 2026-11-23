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

class VercelPathMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        orig = environ.get('HTTP_X_MATCHED_PATH') or environ.get('HTTP_X_FORWARDED_URI')
        p = environ.get('PATH_INFO', '')
        if p in ('/api/index', '/api/index.py', '/api') and orig:
            environ['PATH_INFO'] = orig
        elif p in ('/api/index', '/api/index.py'):
            environ['PATH_INFO'] = '/'
        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathMiddleware(app.wsgi_app)
