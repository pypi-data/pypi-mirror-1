# Copyright 2005-2008 Barry A. Warsaw
#
# This file is part of the Python Replybot.
#
# The Python Replybot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# The Python Replybot is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# The Python Replybot.  If not, see <http://www.gnu.org/licenses/>.

"""An smtpd-based RFC 2821-compliant mail server."""

import os
import re
import sys
import email
import smtpd
import signal
import socket
import mailbox
import asyncore
import optparse

COMMASPACE = ', '



class Channel(smtpd.SMTPChannel):
    def __init__(self, server, conn, addr):
        smtpd.SMTPChannel.__init__(self, server, conn, addr)
        # The base class makes the server attribute private. :(
        self._server = server

    def send(self, data):
        # Silence asynchat/asyncore broken pipe errors.
        try:
            return smtpd.SMTPChannel.send(self, data)
        except socket.error:
            pass



class Server(smtpd.SMTPServer):
    def __init__(self, host, port, maildir):
        smtpd.SMTPServer.__init__(self, (host, port), None)
        self._mailbox = mailbox.Maildir(maildir, email.message_from_file)

    def handle_accept(self):
        conn, addr = self.accept()
        channel = Channel(self, conn, addr)
        # Don't call the base class method, since that would create a second
        # channel, which we don't need.

    def process_message(self, peer, mailfrom, rcpttos, data):
        msg = email.message_from_string(data)
        msg['X-Peer'] = str(peer)
        msg['X-RCPT-To'] = COMMASPACE.join(rcpttos)
        msg['Return-Path'] = mailfrom
        self._mailbox.add(msg)



def parseargs():
    parser = optparse.OptionParser()
    parser.add_option('--host', default='localhost', action='store')
    parser.add_option('--port', type='int')
    parser.add_option('--mbox', action='store')
    options, arguments = parser.parse_args()
    parser.options = options
    parser.arguments = arguments
    return parser



def signal_handler(*ignore):
    # Shut down the asyncore loop.
    asyncore.socket_map.clear()



if __name__ == '__main__':
    # Set up signal handlers for exiting.
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    parser = parseargs()
    server = Server(parser.options.host,
                    parser.options.port,
                    parser.options.mbox)
    asyncore.loop()
    asyncore.close_all()
