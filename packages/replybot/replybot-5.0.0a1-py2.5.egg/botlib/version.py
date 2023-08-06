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

__version__ = '5.0.0a1'
__schema__  = 4

VERSION = __version__

# And as a hex number in the manner of PY_VERSION_HEX
ALPHA = 0xa
BETA  = 0xb
GAMMA = 0xc
# release candidates
RC    = GAMMA
FINAL = 0xf

MAJOR_REV = 5
MINOR_REV = 0
MICRO_REV = 0
REL_LEVEL = ALPHA
# at most 15 beta releases!
REL_SERIAL = 1

HEX_VERSION = ((MAJOR_REV << 24) | (MINOR_REV << 16) | (MICRO_REV << 8) |
               (REL_LEVEL << 4)  | (REL_SERIAL << 0))
