# Register skin directory
from iqpp.plone.rating.config import *
from Products.CMFCore import DirectoryView
DirectoryView.registerDirectory('skins', GLOBALS)

# Register indexes.
import catalog
