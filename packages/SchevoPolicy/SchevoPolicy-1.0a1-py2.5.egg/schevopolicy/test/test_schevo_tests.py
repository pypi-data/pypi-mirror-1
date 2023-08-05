"""Test Schevo's unit tests against restricted databases with
allow-all-operation policies.

For copyright, license, and warranty, see bottom of file.
"""

import sys
from schevo.lib import optimize


from base import class_with_policy

from schevo.test.test_bank import BaseBank
from schevo.test.test_calculated_field_unicode import BaseCalculatedUnicode
from schevo.test.test_change import (
    BaseChangeset,
##     BaseExecuteNotification,
    BaseDistributor,
    )
from schevo.test.test_database_namespace import BaseDatabaseNamespaces
from schevo.test.test_default_values import BaseDefaultValues
from schevo.test.test_entity_extent import BaseEntityExtent
from schevo.test.test_entity_subclass import (
    BaseHiddenBases,
    BaseSameNameSubclasses,
    BaseSubclassTransactionCorrectness,
    )
from schevo.test.test_extent_name_override import BaseOverride
from schevo.test.test_extent_without_fields import BaseExtentWithoutFields
from schevo.test.test_extentmethod import BaseExtentMethod
from schevo.test.test_field_entity import BaseEntity
from schevo.test.test_field_entitylist import BaseFieldEntityList
from schevo.test.test_field_entityset import BaseFieldEntitySet
from schevo.test.test_field_entitysetset import BaseFieldEntitySetSet
from schevo.test.test_field_maps import BaseFieldMaps
from schevo.test.test_icon import BaseFsIconMap
from schevo.test.test_label import BaseDecoration
from schevo.test.test_links import BaseLinks
from schevo.test.test_on_delete import (
    BaseOnDelete,
    BaseOnDeleteKeyRelax,
    )
from schevo.test.test_populate import (
    BasePopulateSimple,
    BasePopulateComplex,
    BasePopulateHidden,
    )
from schevo.test.test_query import BaseQuery
from schevo.test.test_relax_index import BaseRelaxIndex
from schevo.test.test_schema import BaseSchema
from schevo.test.test_transaction import BaseTransaction
from schevo.test.test_transaction_before_after import BaseTransactionBeforeAfter
from schevo.test.test_transaction_field_reorder import (
    BaseTransactionFieldReorder)
from schevo.test.test_transaction_require_changes import (
    BaseTransactionRequireChanges)
from schevo.test.test_view import BaseView


# test_bank
TestBank = class_with_policy(BaseBank)

# test_calculated_field_unicode
TestCalculatedUnicode = class_with_policy(BaseCalculatedUnicode)

# test_change
TestChangeset = class_with_policy(BaseChangeset)
# Commented out since it modifies `db` global directly.
## TestExecuteNotification = class_with_policy(BaseExecuteNotification)
TestDistributor = class_with_policy(BaseDistributor)

# test_database_namespace
TestDatabaseNamespaces = class_with_policy(BaseDatabaseNamespaces)

# test_default_values
TestDefaultValues = class_with_policy(BaseDefaultValues)

# test_entity_extent
TestEntityExtent = class_with_policy(BaseEntityExtent)

# test_entity_subclass
TestHiddenBases = class_with_policy(BaseHiddenBases)
TestSameNameSubclasses = class_with_policy(BaseSameNameSubclasses)
TestSubclassTransactionCorrectness = class_with_policy(
    BaseSubclassTransactionCorrectness)

# test_extent_name_override
TestOverride = class_with_policy(BaseOverride)

# test_extent_without_fields
TestExtentWithoutFields = class_with_policy(BaseExtentWithoutFields)

# test_extentmethod
TestExtentMethod = class_with_policy(BaseExtentMethod)

# test_field_entity
TestEntity = class_with_policy(BaseEntity)
# XXX: For now, disable test_convert.
TestEntity.test_convert = lambda self: None

# test_field_entitylist
TestFieldEntityList = class_with_policy(BaseFieldEntityList)

# test_field_entityset
TestFieldEntitySet = class_with_policy(BaseFieldEntitySet)

# test_field_entitysetset
TestFieldEntitySetSet = class_with_policy(BaseFieldEntitySetSet)

# test_field_maps
TestFieldMaps = class_with_policy(BaseFieldMaps)

# test_icon
TestFsIconMap = class_with_policy(BaseFsIconMap)

# test_label
TestDecoration = class_with_policy(BaseDecoration)

# test_links
TestLinks = class_with_policy(BaseLinks)

# test_on_delete
TestOnDelete = class_with_policy(BaseOnDelete)
TestOnDeleteKeyRelax = class_with_policy(BaseOnDeleteKeyRelax)
# Dummy methods since we don't care about testing internals of
# database formats.
TestOnDelete.internal_cascade_complex_1 = lambda self: None
TestOnDelete.internal_cascade_complex_2 = lambda self: None

# test_populate
TestPopulateSimple = class_with_policy(BasePopulateSimple)
TestPopulateComplex = class_with_policy(BasePopulateComplex)
TestPopulateHidden = class_with_policy(BasePopulateHidden)
# Skip these tests since they access _EntityClass, not part of the
# standard public API for databases.
TestPopulateSimple.test_datalist_simple = lambda self: None
TestPopulateComplex.test_datalist_complex = lambda self: None

# test_query
TestQuery = class_with_policy(BaseQuery)

# test_relax_index
TestRelaxIndex = class_with_policy(BaseRelaxIndex)

# test_schema
TestSchema = class_with_policy(BaseSchema)

# test_transaction
TestTransaction = class_with_policy(BaseTransaction)
# Dummy method since we don't care about testing internals of database
# formats.
TestTransaction.internal_update_entities_1 = lambda self, expected: None
# Skip these tests since they access _entity_field and _EntityClass,
# not part of the standard public API for databases.
TestTransaction.test_create_simple = lambda self: None
TestTransaction.test_extra_fields = lambda self: None
TestTransaction.test_update_simple = lambda self: None
# Skip this test because for now, it's easier to express this test
# inline even though it becomes incompatible with this SchevoPolicy
# test suite.
TestTransaction.test_callable_wrapper = lambda self: None

# test_transaction_before_after
TestTransactionBeforeAfter = class_with_policy(BaseTransactionBeforeAfter)

# test_transaction_field_reorder
TestTransactionFieldReorder = class_with_policy(BaseTransactionFieldReorder)

# test_transaction_require_changes
TestTransactionRequireChanges = class_with_policy(BaseTransactionRequireChanges)

# test_view
TestView = class_with_policy(BaseView)


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
