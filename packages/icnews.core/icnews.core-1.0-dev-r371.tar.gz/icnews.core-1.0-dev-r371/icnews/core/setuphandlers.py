"""Setup handlers
"""

from StringIO import StringIO

from zope.interface import alsoProvides, directlyProvides, directlyProvidedBy
from zope.component import getUtility
from zope.app.component.hooks import setSite
from zope.app.component.interfaces import ISite, IPossibleSite
from Products.CMFCore.utils import getToolByName
from Products.Five.site.localsite import enableLocalSiteHook

import interfaces
from config import HAS_PLONE3

def ensure_site(context):
  """"""
  if not IPossibleSite.providedBy(context):
      if hasattr(context, 'getPhysicalPath'):
          p = '/'.join(context.getPhysicalPath())
      elif hasattr(context, 'getId'):
          p = context.getId()
      elif hasattr(context, 'id'):
          p = id
      else:
          p = str(context)

      raise TypeError('The object, "%s", is not an IPossibleSite' % p)

  if not ISite.providedBy(context):
      enableLocalSiteHook(context)
      setSite(context)

  if not ISite.providedBy(context):
      raise TypeError('Somehow trying to configure "%s" as an ISite '
                      'has failed' % '/'.join(context.getPhysicalPath()))

def setup_site(portal, out):
    """
    """
    alsoProvides(portal, interfaces.IicNewsSite)
    sm = portal.getSiteManager()

def importVarious(context):
  """ Import various settings.

  This provisional handler will be removed again as soon as full handlers
  are implemented for these steps.
  """
  site = context.getSite()
  out = StringIO()
  logger = context.getLogger("icnews.core")

  ensure_site(site)
  setup_site(site, out)

  print >> out, 'Various settings imported.'

  logger.info(out.getvalue())
  return out.getvalue()

