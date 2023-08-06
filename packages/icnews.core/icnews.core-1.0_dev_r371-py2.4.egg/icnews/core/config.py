try:
    import Products.CMFPlone.migrations.v3_0
    HAS_PLONE3 = True
except ImportError:
    HAS_PLONE3 = False

import icnews.core
PACKAGE = icnews.core

PROJECTNAME = "icnews.core"
PACKAGENAME = "icnews.core"

DEPENDENCIES = []

GLOBALS = globals()
