#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Clipin - Process input manipulation tool.

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

import os

STDIN_FILENO = 0
STDOUT_FILENO = 1
STDERR_FILENO = 2

CHILD = 0


class BaseHandler(object):
    """Basic spawn handler."""

    def __init__(self, options=None):
        self.pid = None
        self.master_fd = None
        self.argv = None
        self.options = options

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def _read(self, fd):
        return os.read(fd, 1024)

    def _write(self, fd, data):
        while data:
            n = os.write(fd, data)
            data = data[n:]

    def _spawn(self, argv):
        import pty
        import tty

        self.argv = (argv,) if type(argv) == type('') else argv
        self.pid, self.master_fd = pty.fork()
        if self.pid == CHILD:
            os.execlp(self.argv[0], *self.argv)
            # Never return

        try:
            mode = tty.tcgetattr(STDIN_FILENO)
            tty.setraw(STDIN_FILENO)
            restore = 1
        except tty.error:    # This is the same as termios.error
            restore = 0
        try:
            pty._copy(self.master_fd, self.master_read, self.stdin_read)
        except OSError:
            if restore:
                tty.tcsetattr(STDIN_FILENO, tty.TCSAFLUSH, mode)

        os.close(self.master_fd)
        return os.waitpid(self.pid, 0)[1]

    def start(self):
        """Code to execute before spawning a process."""
        print("Clipin on")

    def close(self):
        """Code to execute when the process ended."""
        print("Clipin off")

    def stdin_read(self, fd):
        """Hijack process' stdin result."""
        return self._read(fd)

    def master_read(self, fd):
        """Hijack process' stdout result."""
        return self._read(fd)

    def stdin_write(self, data):
        """Send data to process' stdin."""
        return self._write(self.master_fd, data)

    def master_write(self, fd, data):
        """Send data to process."""
        return self._write(fd, data)

    def spawn(self, argv):
        """Spawn a new process."""
        return self._spawn(argv)


def spawn(argv, handler=BaseHandler, options=None):
    with handler(options) as h:
        return h.spawn(argv)


if __name__ == "__main__":
    import argparse
    import handler

    parser = argparse.ArgumentParser()
    parser.add_argument('--tcp', action="store_true")
    parser.add_argument('args', nargs='*')
    options = parser.parse_args()

    spawn(
        options.args,
        handler.TCPHandler if options.tcp else BaseHandler,
        options
    )
