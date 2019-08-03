#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Clipin handler - Process input manipulation tool.

    Clipboard Server Project
    Copyright (C) 2019  Sepalani

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from clipin import BaseHandler
from threading import Thread

try:
    import SocketServer
except ImportError:
    import socketserver as SocketServer


class TCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        print("[CLIPIN] New client {}:{}".format(
            *self.client_address
        ))
        data = self.request.recv(1024)
        while data:
            self.server.clipin.stdin_write(data)
            data = self.request.recv(1024)


class TCPHandler(BaseHandler):
    def start(self):
        HOST, PORT = "127.0.0.1", 21000
        self.server = SocketServer.TCPServer((HOST, PORT), TCPRequestHandler)
        print("[CLIPIN] Listening on {}:{}".format(HOST, PORT))
        self.server.clipin = self
        self.server_thread = Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def close(self):
        print("[CLIPIN] Closing...")
        self.server.shutdown()
        self.server.server_close()
