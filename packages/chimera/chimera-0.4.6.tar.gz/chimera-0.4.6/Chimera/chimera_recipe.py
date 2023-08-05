"""
chimera
~~~~~~~~~~~~~~~~~~~~
recipies are image generation programs. They are designed to be simple
to create and use. Each recipie implements policy for creation and
retrival of images it produces.

"""

__author__ = 'Benjamin Saller <bcsaller@objectrealms.net>'
__docformat__ = 'restructuredtext'
__copyright__ = 'Copyright ObjectRealms LLC, 2005.'
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


## SECURITY
## Recipe's can execute arbitrary Python code in an unsafe
## mannor. Only give access to modify a recipe to site managers and
## trusted users. If this flexiblity is too much of a concern the
## Chimera Tool support only allowing FileSystem based recipes to
## execute. This removes some of the Through The Web flexibility of
## the Chimera system, but still allows for the recipe to be invoked
## with all the same flexibility.

class ChimeraRecipe(UniqueObject, atapi.BaseFolder,
                    ActionProviderBase):
    portal_type = meta_type = 'Chimera Recipe'

    # Only Contain Chimera Recipes
    # one day we might name this tool 'images' so that
    # site/images is managed by Chimera. At that point this will
    # have to change to anything with an image interface marker.
    global_allow = 0
    security = ClassSecurityInfo()
    protect  = security.declareProtected

    text_fieldnames = ['text']

    schema = atapi.BaseFolder.schema + atapi.Schema((
        atapi.TextField('recipe',
                        widget=atapi.RichWidget()
                        ),
        ))


    protect(CMFCorePermissions.ModifyPortalContent,
            'setRecipe')
    def setRecipe(self, value, **kwargs):
        """Setting the recipe will change the program used to generate
        images. This is the program that will be exectued when the
        recipe is called.
        """
        if self.aq_inner.aq_parent.getFsOnly(): return
        self.Schema()['recipe'].set(value, **kwargs)
        self._clearCache()

    protect(CMFCorePermissions.View,
            'getRecipe')
    def getRecipe(self):
        v = self.Schema()['recipe'].get(self)
        if v:
            return v
        else:
            rid = self.getId()
            match = getattr(self, "%s_chimera" % rid)
            # The recipe could be an external method
            # a script, or another object in the ZODB, we try to
            # support this as much as is reasonable
            # We see if it has a callable of this recipe name
            if hasattr(match, rid) and callable(getattr(match, rid)):
                match = getattr(match, rid)
            return match

    ## Primary Interface
    protect(CMFCorePermissions.View,
            '__call__')
    def __call__(self, **kwargs):
        """Invoke the recipe as though it were a traditional Zope
        PythonScript. The context supplied will include:
              context - the recipe object
              kwargs  - the set of arguments used to trigger the
                        recipe. The recipe itself must know what to do
                        with these. The conventional arguments would
                        include text=<unicode string> though some
                        recipes might not include even this.

        The return from the script will be an OFS image which
        has already been added to the folder as a cached object.
        """
        if not kwargs: kwargs.update(self.REQUEST.form)
        key = imageadapter.hashKey(**kwargs)
        obj = getattr(self, key, None)
        # Cached version
        if obj is not None: return obj

        # Generate one using the recipe
        recipe = self.getRecipe()

        # we specially look for "text" in kwargs so that we can encode
        obj = recipe(context=self, **kwargs)
        # convert it to an image
        obj = imageadapter.toOFSImage(key, obj,
                                      title=kwargs.get('text', key))

        self._setObject(key, obj)
        # return a version with aq context
        return getattr(self, key)

    def view(self, **kwargs):
        """To see the actual image we an say /chimera/recipe/view?text=xxx"""
        res = self(**kwargs)
        return res.index_html(self.REQUEST, self.REQUEST.RESPONSE)

    ## Internal utility methods
    def _clearCache(self):
        # This will remove all the content of the recipe (which should
        # only contain generated images).
        for oid in self.objectIds():
            self._delObject(oid)




atapi.registerType(ChimeraRecipe)

