"""Policy classes.

For copyright, license, and warranty, see bottom of file.
"""

import sys
from schevo.lib import optimize

from schevopolicy.constant import DENY
from schevopolicy.rdatabase import RestrictedDatabase
from schevopolicy.error import Unauthorized


class Policy(object):

    def __init__(self, db):
        self.db = db

    def __call__(self, context=None):
        """Return a restricted database.

        - `context`: The context, if available, to use when enforcing
          restriction rules.
        """
        return RestrictedDatabase(self, context)

    def attach(self, obj, context):
        """Attach convenience functions and attributes to `obj` based
        on `context`."""
        # Use obj.__dict__ to bypass __setattr__.
        d = obj.__dict__
        def _allow():
            return self.allow(context)
        def _allow_t(extent, entity, t_name):
            return self.allow_t(context, extent, entity, t_name)
        def _allow_v(entity, v_name):
            return self.allow_v(context, entity, v_name)
        def _unauthorized():
            raise Unauthorized('The operation was not authorized.')
        d['_allow'] = _allow
        d['_allow_t'] = _allow_t
        d['_allow_v'] = _allow_v
        d['_context'] = context
        d['_policy'] = self
        d['_unauthorized'] = _unauthorized


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
