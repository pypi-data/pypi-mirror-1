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

"""Internationalization support."""

__metaclass__ = type
__all__ = [
    '_',
    ]


import sys
from string import Template

_missing = object()



class ITemplate(Template):
    idpattern = '[_a-z][_a-z0-9.]*'


class nsdict(dict):
    """Dictionary which substitutes in locals and globals."""
    def __getitem__(self, key):
        if key.startswith('{') and key.endswith('}'):
            key = key[1:-1]
            fmt = '${%s}'
        else:
            fmt = '$%s'
        # Split the key as if it were an attribute path
        parts = key.split('.')
        part0 = parts.pop(0)
        # Now search for the parts, starting with the locals and then trying
        # the globals, in the frame two call sites up.  getframe(0) would be
        # this function, while getframe(1) would be the _() function that
        # calls this function.  We want the one above that.
        frame = sys._getframe(2)
        if frame.f_locals.has_key(part0):
            obj = frame.f_locals[part0]
        elif frame.f_globals.has_key(part0):
            obj = frame.f_globals[part0]
        else:
            return fmt % key
        while parts:
            attr = parts.pop(0)
            obj = getattr(obj, attr, _missing)
            if obj is _missing:
                return fmt % key
        return obj



# Marker for internationalization, currently unimplemented.
def _(s):
    return ITemplate(s).safe_substitute(nsdict())
