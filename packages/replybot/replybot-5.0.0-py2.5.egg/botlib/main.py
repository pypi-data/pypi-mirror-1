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

"""The main function for the command line script."""

__metaclass__ = type
__all__ = [
    'main',
    ]


import os
import sys
import email
import random
import sqlite3
import logging

from email.utils import parseaddr

from botlib import botlog
from botlib.configuration import config
from botlib.database import Database
from botlib.i18n import _
from botlib.options import parseargs
from botlib.reply import do_reply

log = logging.getLogger('replybot')
PROGRAM = sys.argv[0]



def main():
    parser, options, arguments, keywords = parseargs()
    config.parser = parser
    config.options = options
    config.arguments = arguments
    config.keywords = keywords
    # Which configuration file should we load?
    if options.configuration is None:
        bindir = os.path.dirname(PROGRAM)
        files = [
            os.path.join(bindir, 'replybot.cfg'),
            os.path.join(os.path.dirname(bindir), 'etc', 'replybot.cfg'),
            '/etc/replybot.cfg',
            ]
        for filename in files:
            if os.path.exists(filename):
                config.load(filename, options.selector)
                break
        else:
            raise RuntimeError('No configuration file found; use -C')
    else:
        config.load(options.configuration, options.selector)
    # Initialize the logging and database connection.
    botlog.initialize()
    config.db = database = Database(config.database_url)
    # Do immediate + exit arguments
    if options.purge_cache:
        database.do_purges(options.purge_cache)
        return 0
    if options.add_whitelist or options.whitelist_file:
        database.do_whitelist(options.add_whitelist, options.whitelist_file)
        return 0
    # If we got here, then a reply url is required.
    if config.reply_url is None:
        parser.error(_('--reply-url is required'))
    # The main loop
    msg = email.message_from_file(sys.stdin)
    try:
        database.process_message(msg)
    except:
        log.exception('process_message() failed')
        raise
