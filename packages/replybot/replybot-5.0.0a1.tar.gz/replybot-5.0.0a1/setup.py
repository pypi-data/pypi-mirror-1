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

import ez_setup
ez_setup.use_setuptools()

import sys

from botlib import version
from setuptools import setup, find_packages



if sys.hexversion < 0x20500f0:
    print 'The Python Replybot requires at least Python 2.5'
    sys.exit(1)



setup(
    name                    = 'replybot',
    version                 = version.__version__,
    description             = 'The Python Replybot',
    long_description        = """\
The Python Replybot is software to send auto-replies to email messages based
on various criteria, with whitelisting and grace periods.""",
    author                  = 'Barry Warsaw',
    author_email            = 'barry@python.org',
    license                 = 'GPLv3',
    url                     = 'http://launchpad.net/replybot',
    keywords                = 'email',
    packages                = find_packages(),
    include_package_data    = True,
    entry_points            = {
        'console_scripts': ['replybot = botlib.main:main'],
        },
    install_requires        = ['storm'],
    setup_requires          = ['setuptools_bzr'],
    # Optionally use 'nose' for unit test sniffing.
    extras_require          = {
        'nose': ['nose', 'coverage'],
        },
    test_suite              = 'nose.collector',
    )
