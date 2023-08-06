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

"""Configuration file parsing."""

__metaclass__ = type
__all__ = [
    'Configuration',
    'config',
    ]


import logging
import datetime
import ConfigParser


_multiplier = {
    'm' : 'minutes',
    'h' : 'hours',
    'd' : 'days',
    'w' : 'weeks',
    }

COMMA = ','



class Configuration:
    """Global configuration class."""

    def load(self, filename, selector='DEFAULT'):
        """Load the configuration file, using the specified selector.

        :param filename: The configuration file name
        :type filename: string
        :param selector: The section selector name
        :type selector: string
        """
        self._cfg = ConfigParser.SafeConfigParser()
        self._cfg.read(filename)
        # Extract system variables.
        self.database_url   = self._cfg.get('SYSTEM', 'database_url')
        self.log_file       = self._cfg.get('SYSTEM', 'log_file')
        log_level           = self._cfg.get('SYSTEM', 'log_level')
        self.mail_server    = self._cfg.get('SYSTEM', 'mail_server')
        mail_port           = self._cfg.get('SYSTEM', 'mail_port')
        self.mail_user      = self._cfg.get('SYSTEM', 'mail_user')
        self.mail_password  = self._cfg.get('SYSTEM', 'mail_password')
        # Extract variables for the given selector section.
        self.replybot_from      = self._cfg.get(selector, 'replybot_from')
        self.replybot_who       = self._cfg.get(selector, 'replybot_who')
        grace_period            = self._cfg.get(selector, 'grace_period')
        cache_period            = self._cfg.get(selector, 'cache_period')
        self.cache_directory    = self._cfg.get(selector, 'cache_directory')
        self.reply_url          = self._cfg.get(selector, 'reply_url')
        self.content_type       = self._cfg.get(selector, 'content_type')
        self.reply_context      = self._cfg.get(selector, 'reply_context')
        # Post-process
        self.mail_port = int(mail_port)
        self.log_level = getattr(logging, log_level.upper())
        if self.mail_user.capitalize() == 'None':
            self.mail_user = None
        if self.mail_password.capitalize() == 'None':
            self.mail_password = None
        if grace_period[-1] in 'mhdw':
            key = _multiplier[grace_period[-1]]
            val = int(grace_period[:-1])
        else:
            key = 'days'
            val = int(grace_period)
        self.grace_period = datetime.timedelta(**{key: val})
        if cache_period[-1] in 'mhdw':
            key = _multiplier[cache_period[-1]]
            val = int(cache_period[:-1])
        else:
            key = 'days'
            val = int(cache_period)
        self.cache_period = datetime.timedelta(**{key: val})



config = Configuration()
