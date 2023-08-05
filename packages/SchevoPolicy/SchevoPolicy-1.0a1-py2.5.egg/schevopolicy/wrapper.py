"""Schevo policy middleware for WSGI apps.

For copyright, license, and warranty, see bottom of file.
"""

from StringIO import StringIO

from schevo import database
from schevo import schema

from schevopolicy.schema import policy_from_location


def filter_factory(global_conf, **local_conf):
    def filter(app):
        return PolicyWrapper(app, local_conf)
    return filter


class PolicyWrapper(object):
    """Policy wrapper middleware for WSGI apps.

    A PolicyWrapper instance will associate a policy schema with a
    Schevo database that was opened using the ``SchevoWsgi#dbopener``
    middleware. It does the following to do so:

    1. Look for configuration items whose keys match
       ``schevopolicy.db.*`` and ``schevopolicy.policy.*``

       Database and policy names are determined by the matching
       configuration items.

    2. Opens the file given by the ``schevopolicy.db.*`` item as a
       Schevo database.

    3. Applies the policy package given by the
       ``schevopolicy.policy.*`` item to the database, and keeps the
       resulting policy instance.

    4. During WSGI application invocation, a PolicyWrapper attaches
       the following to the WSGI environment:

       * keys corresponding to the ``schevopolicy.db.*`` items, with
         values being the original, unrestricted database instances
         themselves

       * keys correpsonding to the ``schevopolicy.policy.*`` items,
         with values being the policy instances themselves

       * a key ``schevopolicy.policy``, which is a dictionary whose
         keys are the names of each policy and whose values are the
         policy instances

       * a key ``schevopolicy.db``, which is a dictionary whose keys
         are the names of each database and whose values are the
         original, unrestricted database instances

       * a key ``schevopolicy.policywrapper`` whose value is the
         PolicyWrapper instance itself, so that other parts of the
         WSGI stack can call ``open`` and ``close`` methods
    """

    db_key_prefix = 'schevopolicy.db'
    policy_key_prefix = 'schevopolicy.policy'
    name = policy_key_prefix + 'wrapper'
    verbose = False

    def __init__(self, app, config):
        """Create a new PolicyWrapper instance.

        - ``app``: The application to filter.

        - ``config``: The configuration in which to look for database
          keys and filenames.
        """
        verbose = config.get('verbose', 'false').lower()
        self.verbose = (verbose == 'true')
        self._app = app
        dbdict = self._dbdict = {}
        policydict = self._policydict = {}
        environ = self._environ = {
            self.name: self,
            self.db_key_prefix: dbdict,
            self.policy_key_prefix: policydict,
            }
        db_dot_prefix = self.db_key_prefix + '.'
        policy_dot_prefix = self.policy_key_prefix + '.'
        for db_key, db_value in config.iteritems():
            if db_key.startswith(db_dot_prefix):
                db_alias = db_key[len(db_dot_prefix):]
                policy_key = policy_dot_prefix + db_alias
                policy_value = config[policy_key]
                self.open(db_alias, db_value, policy_value)

    def __call__(self, environ, start_response):
        environ.update(self._environ)
        return self._app(environ, start_response)

    def open(self, db_alias, db_filename, policy_packagename, environ=None):
        if self.verbose:
            print '[policywrapper] Opening %r (%r :: %r)' % (
                db_alias, db_filename, policy_packagename)
        # Open database.
        if db_filename.startswith('memory://'):
            db = self._open_memory(db_alias, db_filename)
        else:
            db = self._open_file(db_alias, db_filename)
        self._dbdict[db_alias] = db
        # Create policy.
        policy = policy_from_location(db, policy_packagename)
        self._policydict[db_alias] = policy
        # Store db and policy in the environ we use to update the WSGI
        # environ.
        policy_environ_key = self.policy_key_prefix + '.' + db_alias
        self._environ[policy_environ_key] = policy
        db_environ_key = self.db_key_prefix + '.' + db_alias
        self._environ[db_environ_key] = db
        if environ is not None:
            environ[policy_environ_key] = policy
            environ[db_environ_key] = db

    def _open_memory(self, db_alias, db_filename):
        scheme, resource = db_filename.split('://')
        module_name, version = resource.split('/')
        version = int(version)
        fp = StringIO()
        schema_source = schema.read(module_name, version)
        db = database.open(
            fp=fp, schema_source=schema_source, schema_version=version)
        return db

    def _open_file(self, db_alias, db_filename):
        db = database.open(db_filename)
        return db

    def close(self, db_alias, environ=None):
        if self.verbose:
            print '[policywrapper] Closing %r' % db_alias
        policy_environ_key = self.policy_key_prefix + '.' + db_alias
        db_environ_key = self.db_key_prefix + '.' + db_alias
        db = self._dbdict[db_alias]
        policy = self._policydict[db_alias]
        del self._dbdict[db_alias]
        del self._policydict[db_alias]
        del self._environ[policy_environ_key]
        del self._environ[db_environ_key]
        if environ is not None:
            del environ[policy_environ_key]
            del environ[db_environ_key]
        db.close()


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
