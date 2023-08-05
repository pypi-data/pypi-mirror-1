"""
chimera
~~~~~~~~~~~~~~~~~~~~
zope bindings/accessibility for the Chimera project. This package
provides a tool that can be used to generate and cache images in Zope.

"""

__author__ = 'Benjamin Saller <bcsaller@objectrealms.net>'
__docformat__ = 'restructuredtext'
__copyright__ = 'Copyright ObjectRealms LLC, 2005.'
__license__  = 'The GNU Public License V2+'


from Globals import package_home
from Products.Archetypes import public as atapi
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore import utils as cmf_utils
from Products.CMFCore.DirectoryView import registerDirectory
import config
import sys

# Register Global Tools/Services/Config
# (Skins)
registerDirectory(config.SKINS_DIR, config.GLOBALS)


def initialize(context):
    # Zope will trigger this method which will in turn make the
    # chimera runtime available to it.
    from AccessControl import ModuleSecurityInfo, allow_module
    import chimera.pangocairo
    import chimera.fontconfig
    import chimera.chimera
    import chimera
    allow_module('chimera.pangocairo')
    allow_module('chimera.fontconfig')
    allow_module('chimera.chimera')
    allow_module('chimera')

    #allow_module('chimera.fontconfig')

    #ModuleSecurityInfo('chimera').declarePublic("Chimera")
    #ModuleSecurityInfo('chimera').declarePublic("ChimeraSvg")
    #ModuleSecurityInfo('chimera').declarePublic("ChimeraCairo")

    import chimera_tool
    import chimera_recipe

    types = atapi.listTypes(config.PROJECTNAME)
    content_types, constructors, ftis = atapi.process_types(
        types,
        config.PROJECTNAME)

    cmf_utils.ToolInit(
        '%s Tool' % config.PROJECTNAME,
        tools = (chimera_tool.ChimeraTool,),
        product_name = config.PROJECTNAME,
        icon = "tool.png",
        ).initialize( context )

    cmf_utils.ContentInit(
        config.PROJECTNAME,
        content_types = content_types,
        permission = CMFCorePermissions.AddPortalContent,
        extra_constructors = constructors,
        fti = ftis,
        ).initialize(context)



