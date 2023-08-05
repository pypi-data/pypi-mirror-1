"""Base functions and classes for SchevoPolicy tests.

For copyright, license, and warranty, see bottom of file.
"""

import sys
from schevo.lib import optimize

from dispatch import generic

import louie

import schevo
from schevo.change import Distributor
import schevo.icon
from schevo.test import CreatesSchema
from schevo.test.test_change import BaseDistributor
from schevo.test.test_icon import BaseFsIconMap, TEST_ICONS

from schevopolicy.schema import policy_from_string


ALLOW_ALL = """
    # Allow all operations by default.
    default = ALLOW

    # Do not override any allowance.
    """

NO_CONTEXT = None


@generic()
def class_with_policy(base_class):
    """Return a test class based on base_class that patches it to use
    a restricted database."""


@class_with_policy.when("issubclass(base_class, CreatesSchema)")
def class_with_policy_CreatesSchema(base_class):
    
    class TestClass(base_class):

        _use_db_cache = False

        def _open(self, suffix='', reopening=False):
            db = super(TestClass, self)._open(suffix)
            db_name = 'db' + suffix
            ex_name = 'ex' + suffix
            orig_db_name = 'orig_db' + suffix
            policy = policy_from_string(db, ALLOW_ALL)
            rdb = policy(NO_CONTEXT)
            setattr(self, orig_db_name, db)
            setattr(self, db_name, rdb)
            modname = base_class.__module__
            mod = sys.modules[modname]
            setattr(mod, db_name, rdb)
            setattr(mod, ex_name, rdb.execute)
            return rdb

    TestClass.__name__ = 'Test' + base_class.__name__[4:]
    return TestClass


@class_with_policy.when("issubclass(base_class, BaseDistributor)")
def class_with_policy_BaseFsDistributor(base_class):
    base_class = class_with_policy_CreatesSchema(base_class)

    class TestClass(base_class):

        def setUp(self):
            CreatesSchema.setUp(self)
            louie.reset()
            self.orig_db.dispatch = True
            dist = self.dist = Distributor(self.orig_db)

    TestClass.__name__ = 'Test' + base_class.__name__[4:]
    return TestClass


@class_with_policy.when("issubclass(base_class, BaseFsIconMap)")
def class_with_policy_BaseFsIconMap(base_class):
    base_class = class_with_policy_CreatesSchema(base_class)

    class TestClass(base_class):

        def setUp(self):
            CreatesSchema.setUp(self)
            # Install the filesystem icon plugin to the original database,
            # not to the restricted database.
            schevo.icon.install(self.orig_db, TEST_ICONS)

    TestClass.__name__ = 'Test' + base_class.__name__[4:]
    return TestClass


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
