from redturtle.maps.core.config import SKIN_DIR, GLOBALS
from Products.CMFCore.DirectoryView import registerDirectory

registerDirectory(SKIN_DIR, GLOBALS)

def initialize(context):
    """Initializer called when used as a Zope 2 product."""