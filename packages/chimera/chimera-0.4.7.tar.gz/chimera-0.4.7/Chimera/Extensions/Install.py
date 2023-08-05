from StringIO import StringIO
from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.ZCatalog import manage_addZCatalog
from OFS.ObjectManager import BadRequestException

from Products.Chimera import config


def install(self):
    out = StringIO()

    install_subskin(self, out, config.GLOBALS)

    installTypes(self, out, listTypes(config.PROJECTNAME), config.PROJECTNAME)

    try:
        addTool = self.manage_addProduct[config.PROJECTNAME].manage_addTool
        addTool('Chimera')
    except BadRequestException:
        pass

    print >> out, "Successfully installed %s." % config.PROJECTNAME
    return out.getvalue()
