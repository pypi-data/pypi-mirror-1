"""
chimera
~~~~~~~~~~~~~~~~~~~~
the chimera tool which sits happily in your Zope/Plone site managing
your images for you

"""

__author__ = 'Benjamin Saller <bcsaller@objectrealms.net>'
__docformat__ = 'restructuredtext'
__copyright__ = 'Copyright Benjamin Saller, 2004.'
__license__  = 'The GNU Public License V2+'

from AccessControl import ClassSecurityInfo
from Products.Archetypes import public as atapi
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from ZODB.POSException import ConflictError

from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.utils import UniqueObject

import chimera
import imageadapter

## This tool (and the Recipe workers it contains) interact with
## Chimera in a totally transient way. They only store settings and
## never try to persist and Chimera objects directly.

class ChimeraTool(UniqueObject, atapi.BaseFolder,
                  ActionProviderBase):
    portal_type = meta_type = 'Chimera'
    id = "chimera"

    # Only Contain Chimera Recipes
    # one day we might name this tool 'images' so that
    # site/images is managed by Chimera. At that point this will
    # have to change to anything with an image interface marker.
#    allowed_content_types = [ChimeraRecipe.meta_type,]
    global_allow = 0
    security = ClassSecurityInfo()
    protect  = security.declareProtected

    schema = atapi.BaseFolder.schema + atapi.Schema((
        atapi.BooleanField('fsOnly',
                           default=True,
                           widget=atapi.BooleanWidget(
                                  label = "FileSystem only Recipes",
                                  description = """
                                  When set (and this defaults to true)
                                  even users with permissions to
                                  create new recipies cannot modify
                                  them through the CMS. With this flag
                                  set the original code must be
                                  changed on the FileSystem or altered
                                  in the ZMI directly. Recipies will
                                  all acquire this setting from the
                                  tool.
                                  """),
                           ),
        ))


    def __init__(self):
        atapi.BaseFolder.__init__(self, ChimeraTool.id)
        self.setTitle(ChimeraTool.portal_type)

    protect(CMFCorePermissions.ManagePortal, 'registerImageDirectory')
    def registerImageDirectory(self, directory):
        """Register an image directory that is available to recipies
        held by this tool.
        """
        pass

    protect(CMFCorePermissions.ManagePortal, 'registerFontDirectory')
    def registerFontDirectory(self, fontdir):
        """Update the global font registry to expose an additional
        directory of filesystem fonts to the chimera runtime. Changing
        this in any one tool affects the availability of fonts for all
        the tools.
        """

##     protect(CMFCorePermissions.View, "__call__")
##     def __call__(self, text, font, maxwidth=None):
##         """w/o recipe"""
##         image = chimera.ChimeraText(font, text,
##                                     "black",
##                                     "transparent",
##                                     maxwidth=maxwidth)
##         ## convert text to key? or md5 + title like IM tool?
##         id, image = imageadapter.toOFSImage(text, font, image)
##         # We can reference this for long enough to resolve the request
##         try:
##             self.temp_folder._delObject(id)
##         except:
##             pass
##         self.temp_folder._setObject(id, image)
##         return getattr(self.temp_folder, id)

    protect(CMFCorePermissions.View, "listFontFamilies")
    def listFontFamilies(self):
        return sorted(chimera.listFontFamilies())


atapi.registerType(ChimeraTool)


