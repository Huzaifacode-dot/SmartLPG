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

        # 1. Parse __vercel_path from query string if present (from /:path* wildcard rewrite)
        if '__vercel_path=' in qs:
            params = urllib.parse.parse_qs(qs, keep_blank_values=True)
            if '__vercel_path' in params:
                val = params.pop('__vercel_path')[0]
                if val and val != '/':
                    path_override = '/' + val.lstrip('/')
                else:
                    path_override = '/'
                # Clean up query string so Flask receives clean query parameters
                clean_pairs = []
                for k, vals in params.items():
                    for v in vals:
                        clean_pairs.append(f"{urllib.parse.quote(k)}={urllib.parse.quote(v)}")
                environ['QUERY_STRING'] = '&'.join(clean_pairs)

        # 2. Check x-now-route-matches (Vercel attaches route matches here)
        if not path_override and 'HTTP_X_NOW_ROUTE_MATCHES' in environ:
            try:
                matches = urllib.parse.parse_qs(environ['HTTP_X_NOW_ROUTE_MATCHES'])
                matched_val = matches.get('path', [None])[0] or matches.get('1', [None])[0]
                if matched_val:
                    path_override = '/' + matched_val.lstrip('/')
            except Exception:
                pass

        # 3. Check standard forwarded path headers as fallback
        if not path_override:
            header_cand = (
                environ.get('HTTP_X_FORWARDED_PATH')
                or environ.get('HTTP_X_FORWARDED_URI')
                or environ.get('HTTP_X_VERCEL_FORWARDED_FOR')
                or environ.get('HTTP_X_MATCHED_PATH')
                or environ.get('HTTP_X_VERCEL_MATCHED_PATH')
                or environ.get('REQUEST_URI')
            )
            if header_cand:
                cand_path = header_cand.split('?')[0]
                if cand_path and cand_path not in ('/api/index', '/api/index.py', '/api'):
                    path_override = cand_path

        # 4. Apply resolved path, or fallback to '/' if pointing directly to serverless index
        curr_p = environ.get('PATH_INFO', '')
        if path_override:
            environ['PATH_INFO'] = path_override
        elif curr_p in ('/api/index', '/api/index.py', '/api'):
            environ['PATH_INFO'] = '/'

        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathMiddleware(app.wsgi_app)
