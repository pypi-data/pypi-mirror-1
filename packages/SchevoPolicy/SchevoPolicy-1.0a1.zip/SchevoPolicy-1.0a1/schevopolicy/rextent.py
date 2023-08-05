"""Restricted extent class.

For copyright, license, and warranty, see bottom of file.
"""

import sys
from schevo.lib import optimize

from schevo import base
from schevo.entity import Entity
from schevo.label import label, plural, with_label
from schevo.query import ResultsIterator, ResultsList

from schevopolicy.convert import unrestricted_args
from schevopolicy.error import Unauthorized
from schevopolicy.rentity import RestrictedEntity
from schevopolicy.rtransaction import RestrictedTransaction


class RestrictedExtent(base.Extent):

    def __init__(self, policy, context, rdb, extent):
        policy.attach(self, context)
        self.db = rdb
        self._extent = extent
        self._label = label(extent)
        self._plural = plural(extent)
        self.__doc__ = extent.__doc__
        self.field_spec = extent.field_spec
        self.hidden = extent.hidden
        self.id = extent.id
        self.key_spec = extent.key_spec
        self.name = extent.name
        self.relationships = extent.relationships
        self.q = RestrictedExtentQueries(policy, context, self)
        self.t = RestrictedExtentTransactions(policy, context, self)
        self.x = RestrictedExtentExtenders(policy, context, self)

    def __cmp__(self, other):
        if isinstance(other, RestrictedExtent):
            return cmp(self._extent, other._extent)
        else:
            return cmp(self._extent, other)

    def __contains__(self, entity):
        if isinstance(entity, RestrictedEntity):
            return entity._entity in self._extent
        else:
            return entity in self._extent

    def __getitem__(self, oid):
        return RestrictedEntity(
            self._policy, self._context, self.db, self, self._extent[oid])

    def __iter__(self):
        policy = self._policy
        context = self._context
        db = self.db
        for entity in self._extent:
            yield RestrictedEntity(policy, context, db, self, entity)

    def __len__(self):
        if not self._allow():
            return self._unauthorized()
        return len(self._extent)

    def by(self, *index_spec):
        results = self._extent.by(*index_spec)
        policy = self._policy
        context = self._context
        db = self.db
        def generator():
            for entity in results:
                yield RestrictedEntity(policy, context, db, self, entity)
        return ResultsIterator(generator())

    def enforce_index(self, *index_spec):
        return self._extent.enforce_index(*index_spec)

    def find(self, **criteria):
        if not self._allow():
            self._unauthorized()
        policy = self._policy
        context = self._context
        db = self.db
        return ResultsList(
            RestrictedEntity(policy, context, db, self, entity)
            for entity in self._extent.find(**criteria)
            )

    def findone(self, **criteria):
        if not self._allow():
            self._unauthorized()
        result = self._extent.findone(**criteria)
        if isinstance(result, Entity):
            result = RestrictedEntity(
                self._policy, self._context, self.db, self, result)
        return result

    @property
    def next_oid(self):
        return self._extent.next_oid

    def relax_index(self, *index_spec):
        return self._extent.relax_index(*index_spec)


class RestrictedExtentExtenders(object):
    
    def __init__(self, policy, context, rextent):
        policy.attach(self, context)
        self._x = rextent._extent.x

    def __getattr__(self, name):
        if not self._allow():
            self._unauthorized()
        return getattr(self._x, name)


class RestrictedExtentQueries(object):

    def __init__(self, policy, context, rextent):
        policy.attach(self, context)
        self._db = rextent.db
        self._q = rextent._extent.q

    def __getattr__(self, name):
        if not self._allow():
            self._unauthorized()
        orig_method = getattr(self._q, name)
        @with_label(label(orig_method))
        def method(*args, **kw):
            # Get the original query object.
            query = orig_method(*args, **kw)
            orig_results = query._results
            # Replace its _results method with something that wraps results.
            p = self._policy
            c = self._context
            db = self._db
            extent = db.extent
            def _results():
                # Create a new results object of the same type, and
                # populate it with the original object's results.
                r = orig_results()
                return type(r)(
                    RestrictedEntity(p, c, db, extent(entity._extent), entity)
                    for entity in r
                    )
            query._results = _results
            return query
        return method

    def __iter__(self):
        return iter(self._q)


class RestrictedExtentTransactions(object):

    def __init__(self, policy, context, rextent):
        policy.attach(self, context)
        self._db = rextent.db
        self._extent = rextent._extent
        self._t = rextent._extent.t

    def __getattr__(self, name):
        if not self._allow():
            self._unauthorized()
        method = getattr(self._t, name)
        policy = self._policy
        context = self._context
        @with_label(label(method))
        def tx_method(*args, **kw):
            args, kw = unrestricted_args(args, kw)
            tx = method(*args, **kw)
            return RestrictedTransaction(policy, context, self._db, tx)
        tx_method.__name__ = method.__name__
        return tx_method

    def __iter__(self):
        allow_t = self._allow_t
        extent = self._extent
        return iter(
            name for name in extent.t
            if allow_t(extent, None, name)
            )


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
