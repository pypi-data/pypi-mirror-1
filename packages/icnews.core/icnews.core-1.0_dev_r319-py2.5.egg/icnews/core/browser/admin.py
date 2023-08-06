"""Main admin screen
"""
import os

from Products.Five.browser import BrowserView

from icnews.core import pkg_home

class Overview(BrowserView):
    """ icNews config overview
    """

    def getVersion( self ):
        fh = open( os.path.join( pkg_home, 'version.txt') )
        version_string = fh.read()
        fh.close()
        return version_string

