"""schevopolicy.schema.policy_from_location unit tests.

For copyright, license, and warranty, see bottom of file.
"""

import sys
from schevo.lib import optimize

from schevo.test import EvolvesSchemata

from schevopolicy.schema import policy_from_location


LOCATION = 'schevopolicy.test.test_policy'


SOURCE = """
from schevo.schema import *
schevo.schema.prep(locals())

class Foo(E.Entity):

    name = f.unicode()

    _key(name)
"""


class BasePolicyFromLocation(EvolvesSchemata):
    """Using the same schema source but with two different schema
    versions, tests the loading of associated policy from a location
    on disk.
    """

    schemata = [
        SOURCE,                         # Version 1.
        SOURCE,                         # Version 2.
        ]

    skip_evolution = True


class TestPolicyFromLocation1(BasePolicyFromLocation):
    """The policy associated with version 1 allows creation of new Foo
    entities for all contexts."""

    schema_version = 1

    def test(self):
        policy = policy_from_location(db, LOCATION)
        context = None
        rdb = policy(context)
        assert list(rdb.Foo.t) == ['create']


class TestPolicyFromLocation2(BasePolicyFromLocation):
    """The policy associated with version 2 disallows creation of new
    Foo entities for all contexts."""

    schema_version = 2

    def test(self):
        policy = policy_from_location(db, LOCATION)
        context = None
        rdb = policy(context)
        assert list(rdb.Foo.t) == []


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
