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

"""Parse command line options."""

from __future__ import with_statement

__metaclass__ = type
__all__ = [
    'parseargs',
    ]


from optparse import OptionParser

from botlib import version
from botlib.i18n import _



def parseargs():
    parser = OptionParser(
        version='The Python Replybot v%s' % version.__version__,
        usage=_("""\
%prog [options] [key val [key val ...]]

Send an automatic reply to a message posted to an email address.

This script sends a reply to a message taken from standard input.  The reply
text is fetched from a url specified in a configuration file and cached for a
certain amount of time to reduce network traffic.

The reply text uses $variable expansions as described here:

http://www.python.org/doc/current/lib/node40.html

Substitution variables are taken from the RFC 2822 headers of the original
message (coerced to lower case) and the optional case-sensitive key/value
pairs provided on the command line."""))
    parser.add_option('-C', '--configuration', metavar='FILE',
                      help=_("""\
The configuration file to use, otherwise search for the file in this order:
replybot.cfg in the directory containing the replybot script, replybot.cfg in
a sibling etc directory to the directory where this script lives
(i.e. ../etc/replybot.cfg), the system file /etc/replybot.cfg.  If no
configuration file is found and this option is not given, an error occurs.
See the file replybot.cfg.sample in the source distribution for details."""))
    parser.add_option('-s', '--selector', action='store',
                      default='DEFAULT', metavar='SECTION', help=("""\
SECTION chooses and override section in the configuration file.  Without this,
only the DEFAULT section values will be used."""))
    parser.add_option('-p', '--purge-cache', default=[], metavar='CHOICES',
                      action='append',
                      choices=('notices', 'replies', 'whitelist', 'all'),
                      help=_("""\
This option purges certain information in the replybot's database.  You can
have multiple purge options on the command line.  After a purge, replybot
exits.  Here are the options: `notices' purges the cache of reply messages;
`replies' purges the last reply dates for all recipients; `whitelist' purges
all whitelist flags; `all' combines all the previous purge options."""))
    parser.add_option('-w', '--add-whitelist', default=[], metavar='PATTERN',
                      action='append', help=_("""\
Add a pattern to the whitelist; the pattern can either be an explicit address,
or it can be a regular expression.  Put a ^ at the front of PATTERN to
indicate a regular expression.  Whitelisted addresses will never get an
autoreply.  Multiple -w options can be provided, or use -W to provide a file
of patterns to whitelist.  After processing this option, replybot exits."""))
    parser.add_option('-W', '--whitelist-file', action='store',
                      metavar='FILE', default=None, help=_("""\
Add all the patterns in the file to the whitelist.  Whitelisted addresses will
never get an autoreply.  Patterns in this file must appear one-per line, and
can be in either form accepted by email.Utils.parseaddr(), or prepend the line
with a ^ to indicate a regular expression.  After processing this option,
replybot exits."""))
    parser.add_option('-d', '--debug', default=False, action='store_true',
                      help=_("""\
Put replybot in debug mode.  Everything works except that autoreply emails are
never actually sent."""))
    parser.add_option('-t', '--testing', default=False, action='store_true',
                      help=_("""\
Put replybot in testing mode.  This enables some extra functionality, such as
positive replies being sent to messages with an `X-Ack: Yes' header."""))
    options, arguments = parser.parse_args()
    # Parse key/value pairs
    if len(arguments) % 2:
        parser.error(_('Odd number of key/value pairs'))
    keywords = dict(zip(arguments[::2], arguments[1::2]))
    return parser, options, argument, keywords
