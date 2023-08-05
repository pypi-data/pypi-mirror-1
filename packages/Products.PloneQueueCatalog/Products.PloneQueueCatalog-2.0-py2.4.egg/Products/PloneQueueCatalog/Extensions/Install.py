# Copyright (C) 2004-2007
# Jarn <info@jarn.com>, http://www.jarn.com
#
# Sidnei da Silva <sidnei@x3ng.com>

"""\
This file is an installation script for PloneQueueCatalog
"""

from cStringIO import StringIO

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import CatalogTool

queue_catalog_present = 1
try:
    from Products.QueueCatalog import QueueCatalog
except:
    queue_catalog_present = 0


def installQueueCatalog(self, out):
    """Replace the catalog tool if necessary"""
    portal = getToolByName(self, 'portal_url').getPortalObject()
    p_cat = getToolByName(self, 'portal_catalog')

    if isinstance(p_cat, QueueCatalog):
        out.write(' - Portal Catalog tool already a QueueCatalog')
        return

    new_cat = QueueCatalog()
    new_cat.__dict__.update(p_cat.__dict__)
    new_cat.manage_edit('', location='portal_catalog_real', immediate_removal=1)
    new_cat._p_changed = 1

    setattr(portal, 'portal_catalog', new_cat)
    portal._setObject('portal_catalog_real', aq_base(p_cat))
    objmap = portal._objects
    for info in objmap:
        if info['id'] == 'portal_catalog':
            info['meta_type'] = new_cat.meta_type
    portal._objects = objmap

    out.write(' - Replaced Portal Catalog tool with QueueCatalog')

def install(self):
    out = StringIO()

    # Make sure QueueCatalog is present
    if not queue_catalog_present:
        raise ValueError, 'You need QueueCatalog to use PloneQueueCatalog, get it from http://www.zope.org/Members/ctheune/QueueCatalog/!'

    installQueueCatalog(self, out)
    out.write('Installation completed.\n')
    return out.getvalue()

#
# Uninstall methods
#
def removeQueueCatalog(self, out):
    # Process everything waiting in queue
    # Remove portal_catalog
    # Rename portal_catalog_real to portal_catalog
    """Replace the catalog tool if necessary"""
    portal = getToolByName(self, 'portal_url').getPortalObject()
    p_cat = getToolByName(self, 'portal_catalog')

    if isinstance(p_cat, CatalogTool):
        out.write(' - Portal Catalog tool already a Plone Catalog Tool')
        return

    old_cat = getToolByName(self, 'portal_catalog_real')

    setattr(portal, 'portal_catalog', old_cat)
    portal._delObject('portal_catalog_real')
    objmap = portal._objects
    for info in objmap:
        if info['id'] == 'portal_catalog':
            info['meta_type'] = old_cat.meta_type
    portal._objects = objmap

    out.write(' - Replaced QueueCatalog with Portal Catalog tool')

# The uninstall is used by the CMFQuickInstaller for uninstalling.
def uninstall(self):
    out = StringIO()
    removeQueueCatalog(self, out)
    return out.getvalue()
