from http.server import BaseHTTPRequestHandler, HTTPServer 
from jinja2 import Environment, FileSystemLoader 
import urllib.parse  
import os 
import json 

env = Environment(loader=FileSystemLoader('templates'))

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query = urllib.parse.parse_qs(parsed_path.query)

        if path.startswith('/media/'):
            self.serve_static_file(path)
        elif path == '/':
            self.render_template('index.html')
        elif path == '/about':
            self.render_template('about.html')
        elif path == '/computers':
            try:
                print("Trying to open data.json...")
                with open('data.json', 'r', encoding='utf-8') as f: 
                    data = json.load(f)
                print("Loaded data:", data)
            except Exception as e:
                print("Error loading JSON data:", e) 
                self.send_error(500, "Internal Server Error") 
                return
            self.render_template('computers.html', computers=data['computers'])
        elif path == '/contact':
            self.render_template('contact.html')
        else:
            self.send_error(404, "Page Not Found")

    def do_POST(self):
        if self.path == '/contact':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed_data = urllib.parse.parse_qs(post_data)

            if 'name' in parsed_data and 'message' in parsed_data:
                success = True
            else:
                success = False

            self.render_template('contact.html', success=success)

    def render_template(self, template_name, **context):
        template = env.get_template(template_name)
        html_content = template.render(context)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))

    def serve_static_file(self, path):
    
        file_path = os.getcwd() + path

        try:
            with open(file_path, 'rb') as file:
                self.send_response(200)

                if path.endswith(".css"):
                    self.send_header('Content-type', 'text/css')
                else:
                    self.send_header('Content-type', 'application/octet-stream')

                self.end_headers()

                self.wfile.write(file.read())
        except IOError:
            self.send_error(404, f'File Not Found: {file_path}')



def run(server_class=HTTPServer, handler_class=MyHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
