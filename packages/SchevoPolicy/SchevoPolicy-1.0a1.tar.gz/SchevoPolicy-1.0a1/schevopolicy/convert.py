"""Conversion functions between restricted and non-restricted objects.

For copyright, license, and warranty, see bottom of file.
"""

import sys
from schevo.lib import optimize

from schevopolicy.rentity import RestrictedEntity


def unrestricted_args(args, kw):
    """Return a tuple of (arguments, keyword arguments) based on the
    given arguments and keyword arguments, where RestrictedEntity
    instances have been converted to regular entity instances.

    XXX: Does not handle EntityList, EntitySet, or EntitySetSet
    values.
    """
    newargs = []
    newkw = {}
    for arg in args:
        if isinstance(arg, RestrictedEntity):
            arg = arg._entity
        newargs.append(arg)
    for key, value in kw.iteritems():
        if isinstance(value, RestrictedEntity):
            value = value._entity
        newkw[key] = value
    return (newargs, newkw)


optimize.bind_all(sys.modules[__name__])  # Last line of module.


# Copyright (C) 2001-2007 Orbtech, L.L.C.
#
# Schevo
# http://schevo.org/
#
# Orbtech
# Saint Louis, MO
# http://orbtech.com/
#
# This toolkit is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This toolkit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
