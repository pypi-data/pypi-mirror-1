# -*- coding: utf-8 -*-
# Register our skins directory - this makes it available via portal_skins.
from Products.CMFCore.DirectoryView import registerDirectory
from config import GLOBALS

from Products.CMFCore import utils
from Globals import package_home
from os.path import dirname

# temporarily add the path to the namespace package to the products path,
# so that the directory views are set up correctly
ppath = utils.ProductsPath
utils.ProductsPath.append(dirname(package_home(GLOBALS)))
registerDirectory('skins', GLOBALS)
utils.ProductsPath = ppath

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
