# Copyright (C) 2004-2007
# Jarn <info@jarn.com>, http://www.jarn.com

import sys

from AccessControl import getSecurityManager, ClassSecurityInfo
try:
    from Products.CMFCore.permissions import View
except ImportError:
    # CMF < 1.6
    from Products.CMFCore.CMFCorePermissions import View

from AccessControl.Permissions import manage_zcatalog_entries
from AccessControl.Permissions import view_management_screens

from Products.QueueCatalog import QueueCatalog

# Monkeypatch QueueCatalog

# The queue needs to double as catalog tool, and has to work when scripts
# try to add and remove indexes.
# Add all methods that should be passed on to the real portal_catalog.
_zcatalog_methods = \
    { 'manage_addIndex':1
    , 'delIndex':1
    , 'addIndex':1
    , 'manage_addColumn':1
    , 'delColumn':1
    , 'addColumn':1
    , 'getIndexObjects':1
    , 'unrestrictedSearchResults':1
    , 'manage_convertIndexes':1
    , 'catalog_object':0
    
    # might be required
    , '_listAllowedRolesAndUsers':1
    , 'migrateIndexes':1
    , '_createTextIndexes':1
    , '_removeIndex':1
    , 'enumerateIndexes':1
    , 'enumerateColumns':1
    , 'enumerateLexicons':1
    
    # plone 3.0 requires
    , 'getCounter':1
    }

# # Need a trick here to getting to the module and update the _zcatalog_methods
module = sys.modules[QueueCatalog.__module__]
module._zcatalog_methods.update(_zcatalog_methods)

def indexObject(self, object, idxs=[]):
    """Add to catalog. Patched to allow specifying indexes
    """
    self.catalog_object(object, self.uidForObject(object), idxs)

patch1 = 0
if not hasattr(QueueCatalog, '_qc_indexObject'):
    from Products.QueueCatalog import QueueCatalog
    QueueCatalog._qc_indexObject = QueueCatalog.indexObject
    QueueCatalog.indexObject = indexObject
    security = getattr(QueueCatalog, 'security', ClassSecurityInfo())
    security.declarePrivate('indexObject')
    security.apply(QueueCatalog)
    patch1 = 1

# XXX pghandler discarded
# update_metadata is ignored by QC
def catalog_object(self, obj, uid=None, idxs=None, update_metadata=1,
                   pghandler=None):
    """Patched to allow specifying indexes as in the plone catalog tool,
    update_metadata and pghandler. Discard pghandler for now
    """
    self._qc_catalog_object(obj, uid=uid, idxs=idxs, update_metadata=update_metadata)
    obj._p_deactivate()

patch2 = 0
if not hasattr(QueueCatalog, '_qc_catalog_object'):
    from Products.QueueCatalog import QueueCatalog
    QueueCatalog._qc_catalog_object = QueueCatalog.catalog_object
    QueueCatalog.catalog_object = catalog_object
    security = getattr(QueueCatalog, 'security', ClassSecurityInfo())
    security.declareProtected(manage_zcatalog_entries, 'catalog_object')
    security.apply(QueueCatalog)
    patch2 = 1

patch3 = 0
if not hasattr(QueueCatalog, 'readonly_while_indexing'):
    from Products.QueueCatalog import QueueCatalog
    QueueCatalog.readonly_while_indexing = False
    patch3 = 1

def reindexObject(self, object, idxs=[], update_metadata=1, uid=None):
    """Update catalog after object data has changed.

    Patched to allow update_metadata
    """
    #import pdb; pdb.set_trace()
    self.catalog_object(object, uid or self.uidForObject(object), idxs=idxs,
                        update_metadata=update_metadata) 

patch4 = 0
if not hasattr(QueueCatalog, '_qc_reindexObject'):
    from Products.QueueCatalog import QueueCatalog
    QueueCatalog._qc_reindexObject = QueueCatalog.reindexObject
    QueueCatalog.reindexObject = reindexObject
    security = getattr(QueueCatalog, 'security', ClassSecurityInfo())
    security.declarePrivate('reindexObject')
    security.apply(QueueCatalog)
    patch4 = 1
