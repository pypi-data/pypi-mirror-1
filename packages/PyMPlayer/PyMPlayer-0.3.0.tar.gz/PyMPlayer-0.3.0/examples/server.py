#!/usr/bin/env python
# $Id: server.py 357 2008-01-24 10:19:17Z darwin $
#
# Copyright (C) 2007-2008  UP EEE Computer Networks Laboratory
# Copyright (C) 2007-2008  Darwin M. Bautista <djclue917@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""PyMPlayer Server Daemon"""

import sys
import socket
import signal
try:
    from pymplayer import Server
except ImportError, msg:
    sys.exit(msg)


def main():
    try:
        server = Server(port=1025, max_conn=2)
    except socket.error, msg:
        sys.exit(msg)
    server.args = sys.argv[1:]
    signal.signal(signal.SIGTERM, lambda s, f: server.stop())
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()


if __name__ == "__main__":
    main()
