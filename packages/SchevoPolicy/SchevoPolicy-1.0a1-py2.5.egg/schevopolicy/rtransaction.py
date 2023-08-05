"""Restricted transaction class.

For copyright, license, and warranty, see bottom of file.
"""

import sys
from schevo.lib import optimize

from schevo import base
from schevo.entity import Entity
from schevo.label import label

from schevopolicy.rentity import RestrictedEntity


class RestrictedTransaction(base.Transaction):

    def __init__(self, policy, context, rdb, transaction):
        policy.attach(self, context)
        # Update __dict__ directly due to __setattr__.
        d = self.__dict__
        d.update(dict(
            _db = rdb,
            _tx = transaction,
            _field_spec = transaction._field_spec,
            _inversions = transaction._inversions,
            _label = label(transaction),
            # XXX: Make a separate restricted namespace for .sys?
            sys = transaction.sys,
            # XXX: Make a separate restricted namespace for .x?
            x = transaction.x,
            ))
        # Need to do this in two passes, since the constructor for
        # this relies on certain attributes being in place already.
        d['f'] = RestrictedTransactionFields(policy, context, self)
        # TODO:
        #
        # For each entity field in the transaction, make sure that its
        # value is properly transformed.

    def __getattr__(self, name):
        if not self._allow():
            self._unauthorized()
        if name not in self._field_spec:
            raise AttributeError('Field %r not in %r' % (name, self))
##         f = self._tx.f[name]
##         # Copy the field if it is an entity field, and transform it.
##         if f.may_store_entities:
##             f = f.copy()
##             db = self._db
##             policy = self._policy
##             context = self._context
##             extent = db.extent
##             def to_rentity(e):
##                 return RestrictedEntity(
##                     policy, context, db, extent(e._extent), e)
##             f._transform(to_rentity)
##         return f.get()
        value = getattr(self._tx, name)
        if isinstance(value, Entity):
            # Get restricted extent for the entity.
            db = self._db
            rextent = db.extent(value._extent)
            value = RestrictedEntity(
                self._policy, self._context, db, rextent, value)
        return value

    def __repr__(self):
        return '<restricted %r>' % self._tx

    def __setattr__(self, name, value):
        if not self._allow():
            self._unauthorized()
        tx = self._tx
        if name in self._field_spec:
            # Convert to RestrictedEntity as necessary.
            # XXX: Short-term code; need to generalize this to support
            # EntityList etc.
            if isinstance(value, RestrictedEntity):
                # Get regular entity for this rentity.
                value = value._entity
            return setattr(tx, name, value)
        else:
            return setattr(self, name, value)

    @property
    def _changes(self):
        return self._tx._changes
        
    @property
    def _executed(self):
        return self._tx._executed

    @property
    def _label(self):
        return label(self._tx)

    def _undo(self):
        tx = self._tx._undo()
        if tx is None:
            return None
        else:
            return RestrictedTransaction(
                self._policy, self._context, self._db, tx)


class RestrictedTransactionFields(object):

    def __init__(self, policy, context, rtx):
        policy.attach(self, context)
        self._db = rtx._db
        self._f = rtx._tx.f

    def __delattr__(self, name):
        delattr(self._f, name)

    def __getattr__(self, name):
        f = self._f
        field = getattr(f, name)
        # Copy the field if it is an entity field, and transform it.
        if field.may_store_entities:
            field = field.copy()
            db = self._db
            policy = self._policy
            context = self._context
            extent = db.extent
            def to_rentity(e):
                return RestrictedEntity(
                    policy, context, db, extent(e._extent), e)
            field._transform(to_rentity)
        return field

    def __iter__(self):
        return iter(self._f)


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
