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

"""Set up logging."""

__metaclass__ = type
__all__ = [
    'initialize',
    ]


import os
import errno
import logging

LOGFMT = '%(asctime)s (%(process)d) %(message)s'



def initialize(config):
    """Initialize the system.

    :param config: The configuration object
    :type config: Configuration
    """
    logging.basicConfig()
    log = logging.getLogger('replybot')
    log.setLevel(config.log_level)
    log.propagate = False
    if config.log_file == 'Console':
        handler = logging.StreamHandler()
    else:
        try:
            os.makedirs(os.path.dirname(config.log_file), 02700)
        except OSError, error:
            if error.errno != errno.EEXIST:
                raise
        # Create the log directory if it doesn't yet exist
        handler = logging.FileHandler(config.log_file)
    formatter = logging.Formatter(LOGFMT)
    handler.setFormatter(formatter)
    log.addHandler(handler)
