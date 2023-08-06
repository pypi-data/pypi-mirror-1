# CMF imports
from Products.CMFCore.DirectoryView import registerDirectory

# Product imports
from config import GLOBALS, SKINS_DIR

registerDirectory(SKINS_DIR, GLOBALS)


def initialize(context):
    ##Import Types here to register them
    # No types in this product.
    pass
