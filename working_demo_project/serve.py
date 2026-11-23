#!/usr/bin/env python3
"""
Local development server for Smart Gas Refill Predictor.
Runs a local HTTP server with correct MIME types and SPA fallback.
"""
import http.server
import socketserver
import os
import sys
import webbrowser

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Enable CORS for local testing if needed
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

    def do_GET(self):
        # SPA fallback: if file does not exist and no extension, serve index.html
        path = self.translate_path(self.path)
        if not os.path.exists(path) and '.' not in os.path.basename(path):
            self.path = '/index.html'
        return super().do_GET()

def run_server():
    # Allow address reuse
    socketserver.TCPServer.allow_reuse_address = True
    
    # Try preferred port or next available
    port = PORT
    for attempt in range(5):
        try:
            with socketserver.TCPServer(("", port), Handler) as httpd:
                print("=" * 65)
                print("Smart Gas Refill Predictor - Local Backup Server")
                print(f"Serving locally from: {DIRECTORY}")
                print(f"URL: http://127.0.0.1:{port}")
                print("Press Ctrl+C to stop the server.")
                print("=" * 65)
                httpd.serve_forever()
                break
        except OSError as e:
            if attempt < 4:
                port += 1
            else:
                print(f"Error binding to port: {e}")
                sys.exit(1)

if __name__ == "__main__":
    run_server()
