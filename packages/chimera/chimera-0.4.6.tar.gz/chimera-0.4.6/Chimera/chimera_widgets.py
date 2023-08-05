"""Helpful widgets to do things with Chimera from Archetypes
"""


import Products.Archetypes.public as atapi



class ChimeraImageWidget(atapi.StringWidget):
    _properties = atapi.StringWidget._properties.copy()
    _properties.update({
        # We show a generated image
        # But we edit the original string
        # It might be nice to allow for recipe
        # selection in the widget and store this
        # as an additional attribute
        # for now its in the code
        'macro_view' : 'chimera_image_widget',
        'macro_edit' : 'widgets/string',
        'recipe' : None,
        'recipe_over' : None,
        })



from Products.Archetypes.Registry import registerPropertyType
from Products.Archetypes.Registry import registerWidget

registerWidget(ChimeraImageWidget,
               title="ChimeraImage",
               description=("Render the text value of field using a"
                            "chimera recipe"),
               used_for=('Products.Archetypes.Field.StringField',)
               )
registerPropertyType('recipe', 'string', ChimeraImageWidget)
registerPropertyType('recipe_over', 'string', ChimeraImageWidget)


