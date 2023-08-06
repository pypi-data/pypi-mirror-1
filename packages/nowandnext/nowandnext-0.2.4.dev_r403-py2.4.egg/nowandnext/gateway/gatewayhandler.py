import BaseHTTPServer


class gatewayhandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/plain")
        s.end_headers()
        
    def do_GET(s):
        """Respond to a GET request."""
        
        request_string = s.raw_requestline
        
        s.send_response(200)
        s.send_header("Content-type", "text/plain")
        s.end_headers()
        s.wfile.write("ok ")
        