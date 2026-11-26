import os
import sys
import urllib.parse

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
        qs = environ.get('QUERY_STRING', '')
        path_override = None

        # 1. Parse __vercel_path from query string if present
        if '__vercel_path=' in qs:
            params = urllib.parse.parse_qs(qs, keep_blank_values=True)
            if '__vercel_path' in params:
                val = params.pop('__vercel_path')[0]
                if val:
                    path_override = '/' + val.lstrip('/')
                else:
                    path_override = '/'
                # Clean up query string
                pairs = []
                for k, vals in params.items():
                    for v in vals:
                        pairs.append(f"{urllib.parse.quote(k)}={urllib.parse.quote(v)}")
                environ['QUERY_STRING'] = '&'.join(pairs)

        # 2. Check headers as fallback
        if not path_override:
            orig = (
                environ.get('HTTP_X_FORWARDED_URI')
                or environ.get('HTTP_X_MATCHED_PATH')
                or environ.get('HTTP_X_VERCEL_MATCHED_PATH')
                or environ.get('REQUEST_URI')
            )
            if orig:
                path_only = orig.split('?')[0]
                if path_only and path_only not in ('/api/index', '/api/index.py', '/api'):
                    path_override = path_only

        # 3. Apply resolved path or default to '/'
        if path_override:
            environ['PATH_INFO'] = path_override
        else:
            p = environ.get('PATH_INFO', '')
            if p in ('/api/index', '/api/index.py', '/api'):
                environ['PATH_INFO'] = '/'

        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathMiddleware(app.wsgi_app)
