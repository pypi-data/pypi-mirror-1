# Copyright (C) 2004-2007
# Jarn <info@jarn.com>, http://www.jarn.com

try:
    from Products.QueueCatalog import QueueCatalog
    import QueueCatalogPatches
except:
    # Don't try to monkeypatch nonexisting class
    pass

def initialize(context):
    pass
