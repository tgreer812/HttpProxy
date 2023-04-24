import http.server
import socketserver
import http.client
import ssl
import urllib.parse
import threading

# Request and response hooks
def request_hook(request: http.client.HTTPRequest) -> http.client.HTTPRequest:
    # Modify the request object as needed
    return request

def response_hook(response: http.client.HTTPResponse) -> http.client.HTTPResponse:
    # Modify the response object as needed
    return response

class ProxyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def handle_request(self):
        url = urllib.parse.urlparse(self.path)
        target_host = url.netloc
        target_path = url.path

        if url.query:
            target_path += '?' + url.query

        # Prepare the request to forward to the target server
        request = http.client.HTTPRequest(
            target_path,
            method=self.command,
            headers=self.headers,
            http_version=self.request_version
        )

        # Apply the request hook
        request = request_hook(request)

        # Send the request to the target server
        if url.scheme == 'https':
            target_connection = http.client.HTTPSConnection(target_host)
        else:
            target_connection = http.client.HTTPConnection(target_host)

        target_connection.request(request.method, target_path, headers=request.headers)

        # Retrieve the response from the target server
        target_response = target_connection.getresponse()

        # Apply the response hook
        target_response = response_hook(target_response)

        # Send the response back to the client (Chrome)
        self.send_response(target_response.status, target_response.reason)
        for header, value in target_response.getheaders():
            self.send_header(header, value)
        self.end_headers()
        self.wfile.write(target_response.read())

    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def do_HEAD(self):
        self.handle_request()

    def do_PUT(self):
        self.handle_request()

    def do_DELETE(self):
        self.handle_request()

    def do_CONNECT(self):
        self.send_response(200, 'Connection established')
        self.end_headers()

        target_host, target_port = self.path.split(':')

        target = (target_host, int(target_port))
        target_socket = socket.create_connection(target)

        self.connection = ssl.wrap_socket(
            self.connection,
            keyfile=None, certfile=None, server_side=True,
            cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_SSLv23)

        self.rfile = self.connection.makefile('rb', self.rbufsize)
        self.wfile = self.connection.makefile('wb', self.wbufsize)

        def forward(src, dst):
            while True:
                data = src.recv(4096)
                if len(data) == 0:
                    break
                dst.sendall(data)

        client_thread = threading.Thread(target=forward, args=(self.connection, target_socket))
        server_thread = threading.Thread(target=forward, args=(target_socket, self.connection))

        client_thread.start()
        server_thread.start()

        client_thread.join()
        server_thread.join()

        self.connection.shutdown(socket.SHUT_RDWR)
        self.connection.close()

if __name__ == '__main__':
    PORT = 8080
    with socketserver.ThreadingTCPServer(("", PORT), ProxyHTTPRequestHandler) as httpd:
        print(f"Serving on port {PORT}")
        httpd.serve_forever()
