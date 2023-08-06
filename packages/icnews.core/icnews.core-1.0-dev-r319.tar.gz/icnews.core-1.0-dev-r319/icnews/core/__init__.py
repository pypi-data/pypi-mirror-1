import os, sys
from Globals import package_home

pkg_home = package_home( globals() )
lib_path = os.path.join( pkg_home, 'lib' )

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
