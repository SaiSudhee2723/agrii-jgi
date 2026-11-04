import http.server
import socketserver
import os
import mimetypes

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class GeosenseHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

    def do_GET(self):
        # Clean URLs support
        parsed_path = self.path.split('?')[0].rstrip('/')
        if parsed_path == '':
            self.path = '/index.html'
        elif parsed_path == '/login':
            self.path = '/login.html'
        elif parsed_path == '/register':
            self.path = '/register.html'
        elif parsed_path == '/dashboard':
            self.path = '/dashboard.html'
        elif parsed_path == '/auth/callback':
            self.path = '/auth/callback.html'
        elif not os.path.splitext(parsed_path)[1]:
            # check if .html exists
            potential_html = os.path.join(DIRECTORY, parsed_path.lstrip('/') + '.html')
            if os.path.exists(potential_html):
                self.path = parsed_path + '.html'

        return super().do_GET()

if __name__ == '__main__':
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), GeosenseHandler) as httpd:
        print(f"Geosense Frontend running at http://localhost:{PORT}")
        httpd.serve_forever()
