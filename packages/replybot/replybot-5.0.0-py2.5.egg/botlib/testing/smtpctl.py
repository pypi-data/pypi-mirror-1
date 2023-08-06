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

__metaclass__ = type
__all__ = [
    'Controller',
    ]


import os
import sys
import time
import random
import shutil
import signal
import socket
import mailbox
import datetime
import tempfile

from email import message_from_file
from pkg_resources import resource_filename



class Controller:
    """Manage an SMTP server child process."""

    def __init__(self):
        # Create a temporary directory for the mailbox.
        self._tempdir = tempfile.mkdtemp()
        # Use a subdirectory which does not yet exist so that Maildir will
        # create the necessary subdirectories.
        self._maildir = os.path.join(self._tempdir, 'mailbox')
        self._mailbox = mailbox.Maildir(self._maildir, message_from_file)
        self._pid = None
        self.port = random.randint(10000, 20000)

    def _command(self, command):
        s = socket.socket()
        s.connect(('localhost', self.port))
        s.setblocking(0)
        s.send(command + '\r\n')
        s.close()

    def start(self):
        """Start the child process listening for SMTP."""
        self._pid = pid = os.fork()
        if pid == 0:
            # Child.
            os.execl(sys.executable, sys.executable,
                     resource_filename('botlib.testing', 'smtpsrv.py'),
                     '--host', 'localhost',
                     '--port', str(self.port),
                     '--mbox', self._maildir)
            os._exit(1)
        # Parent.  Wait until the child is listening.
        until = datetime.datetime.now() + datetime.timedelta(seconds=5)
        while datetime.datetime.now() < until:
            try:
                self._command('QUIT')
                return
            except socket.error:
                time.sleep(0.5)
        raise RuntimeError('no smtp listener')

    def stop(self):
        """Stop the child process."""
        os.kill(self._pid, signal.SIGTERM)
        os.waitpid(self._pid, 0)
        shutil.rmtree(self._tempdir, True)

    def reset(self):
        self._mailbox.clear()

    @property
    def messages(self):
        return [message for message in self._mailbox]
