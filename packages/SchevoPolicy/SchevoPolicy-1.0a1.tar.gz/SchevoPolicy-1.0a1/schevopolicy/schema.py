"""Policy schema support.

Everything in here is imported by all policy schemata.

For copyright, license, and warranty, see bottom of file.
"""

__all__ = [
    'ALLOW',
    'DENY',
    'schevopolicy',
    ]


from textwrap import dedent
import threading

from dispatch import generic, strategy

from schevo.lib.module import from_string, forget, remember
import schevo.schema

import schevopolicy
from schevopolicy.constant import ALLOW, DENY
from schevopolicy.policy import Policy


# 'import_lock' is a lock that is acquired during a schema import,
# then released when the import is finished.  It is used to prevent
# the schevo.schema.* namespace from being clobbered if multiple
# threads are importing schemata simultaneously.
import_lock = threading.Lock()


def start(policy):
    """Lock policy schema importing."""
    import_lock.acquire()


def prep(namespace):
    """Add syntax support magic to the policy schema namespace.

    At the top of each policy schema, the following two lines perform
    the magic::

      from schevopolicy.schema import *
      schevopolicy.schema.prep(locals())
    """
    # Create new generic functions to attach to the policy module's
    # namespace.
    @generic()
    def allow(db, context):
        """Return True if any operation should be allowed."""
    @generic()
    def allow_t(db, context, extent, entity, t_name):
        """Return True if the transaction should be allowed."""
    @generic()
    def allow_v(db, context, entity, v_name):
        """Return True if the transaction should be allowed."""
    # Attach those functions to the policy module's namespace.
    namespace['allow'] = allow
    namespace['allow_t'] = allow_t
    namespace['allow_v'] = allow_v


def finish(policy, schema_module=None):
    """Unlock the policy schema import mutex and return the policy
    schema."""
    if schema_module is None:
        # `finish` is called with no `schema_module` if something
        # failed during import.
        import_lock.release()
        return
    try:
        # Attach wrappers for the generic functions to the policy
        # instance itself.
        db = policy.db
        allow = schema_module.allow
        allow_t = schema_module.allow_t
        allow_v = schema_module.allow_v
        def policy_allow(context):
            return allow(db, context)
        def policy_allow_t(context, extent, entity, t_name):
            return allow_t(db, context, extent, entity, t_name)
        def policy_allow_v(context, entity, v_name):
            return allow_v(db, context, entity, v_name)
        policy.allow = policy_allow
        policy.allow_t = policy_allow_t
        policy.allow_v = policy_allow_v
        # Make sure those functions use the default policy defined by
        # the policy schema.
        default = schema_module.default
        @allow.when(strategy.default)
        def allow(db, context):
            return default
        @allow_t.when(strategy.default)
        def allow_t(db, context, extent, entity, t_name):
            return default
        @allow_v.when(strategy.default)
        def allow_v(db, context, entity, v_name):
            return default
    finally:
        import_lock.release()


PREAMBLE = """\
from schevopolicy.schema import *
schevopolicy.schema.prep(locals())
"""


counter = 0
def next_name():
    """Return the next policy module name for an imported policy schema."""
    global counter
    cur = counter
    counter += 1
    return 'schevopolicy-module-%i' % cur


def policy_from_location(db, location):
    source = schevo.schema.read(location, db.version)
    return policy_from_source(db, source)
    

def policy_from_source(db, source):
    policy = Policy(db)
    start(policy)
    module = from_string(source, next_name())
    remember(module)
    finish(policy, module)
    return policy


def policy_from_string(db, body):
    source = PREAMBLE + dedent(body)
    return policy_from_source(db, source)


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
