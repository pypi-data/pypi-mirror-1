"""
colors
~~~~~~~~~~~~~~~~~~~~
the colors to numbers mapping code

"""

__author__ = 'Benjamin Saller <bcsaller@objectrealms.net>'
__docformat__ = 'restructuredtext'
__copyright__ = 'Copyright ObjectRealms, LLC. 2005'
__license__  = 'The GNU Public License V2+'


def parseColorToRGBA(color, masterAlpha=1.0):
    """ Parse (r,g,b)/#rrggbb(aa)/'color' to (r,g,b,a)
    as doubles.
    """
    if isinstance(color, list):
        color = tuple(color)

    # parse a tuple with 3 or 4 elements
    if isinstance(color, tuple):
        #does it have alpha?
        if len(color) == 3: color =  color + (masterAlpha,)
        if len(color) != 4: raise ValueError(color)
        return color

    # parse color names
    if color.startswith('#'): return colorStringToDoubles(color)
    else: return colortable[color]


def colorStringToTuple(color):
    """string to color tuple (#rrggbb -> (r,g,b,a))
    """
    color = color[1:]               # strip the '#'
    c = int('0x'+ color[:6] ,16)    # convert to a hex
    if len(color) == 8: a = int('0x' + color[6:8], 16)
    else: a = 255                   # assume solid
    color = ( c>>16, (c>>8)&255, c&255, a)
    return color

def _clamp(v):
    if isinstance(v, int) and v > 1:
        v = v/255.0
    return v

def colorTupleToDoubles(rgba):
    # convert an rgba 0-255 tuple to 0.0 - 1.0 argb tuple
    return tuple(_clamp(c) for c in rgba)

def colorStringToDoubles(color):
    return colorTupleToDoubles(colorStringToTuple(color))


# Thanks to Christian Heimes for the colortable
# included from a pre-Chimera version of this code

_colortable = [
    # transparent images
    ('transparent', '#ffffff00'),
    # standard vga color table (16)
    ('black', '#000000'),
    ('gray', '#808080'),
    ('maroon', '#800000'),
    ('red', '#FF0000'),
    ('green', '#008000'),
    ('lime', '#00FF00'),
    ('olive', '#808000'),
    ('yellow', '#FFFF00'),
    ('navy', '#000080'),
    ('blue', '#0000FF'),
    ('purple', '#800080'),
    ('fuchsia', '#FF00FF'),
    ('teal', '#008080'),
    ('aqua', '#00FFFF'),
    ('silver', '#C0C0C0'),
    ('white', '#FFFFFF'),
    # netscape color table (216)
    ('aliceblue', '#F0F8FF'),
    ('antiquewhite', '#FAEBD7'),
    ('aquamarine', '#7FFFD4'),
    ('azure', '#F0FFFF'),
    ('beige', '#F5F5DC'),
    ('blueviolet', '#8A2BE2'),
    ('brown', '#A52A2A'),
    ('burlywood', '#DEB887'),
    ('cadetblue', '#5F9EA0'),
    ('chartreuse', '#7FFF00'),
    ('chocolate', '#D2691E'),
    ('coral', '#FF7F50'),
    ('cornflowerblue', '#6495ED'),
    ('cornsilk', '#FFF8DC'),
    ('crimson', '#DC143C'),
    ('darkblue', '#00008B'),
    ('darkcyan', '#008B8B'),
    ('darkgoldenrod', '#B8860B'),
    ('darkgray', '#A9A9A9'),
    ('darkgreen', '#006400'),
    ('darkkhaki', '#BDB76B'),
    ('darkmagenta', '#8B008B'),
    ('darkolivegreen', '#556B2F'),
    ('darkorange', '#FF8C00'),
    ('darkorchid', '#9932CC'),
    ('darkred', '#8B0000'),
    ('darksalmon', '#E9967A'),
    ('darkseagreen', '#8FBC8F'),
    ('darkslateblue', '#483D8B'),
    ('darkslategray', '#2F4F4F'),
    ('darkturquoise', '#00CED1'),
    ('darkviolet', '#9400D3'),
    ('deeppink', '#FF1493'),
    ('deepskyblue', '#00BFFF'),
    ('dimgray', '#696969'),
    ('dodgerblue', '#1E90FF'),
    ('firebrick', '#B22222'),
    ('floralwhite', '#FFFAF0'),
    ('forestgreen', '#228B22'),
    ('gainsboro', '#DCDCDC'),
    ('ghostwhite', '#F8F8FF'),
    ('gold', '#FFD700'),
    ('goldenrod', '#DAA520'),
    ('greenyellow', '#ADFF2F'),
    ('honeydew', '#F0FFF0'),
    ('hotpink', '#FF69B4'),
    ('indianred', '#CD5C5C'),
    ('indigo', '#4B0082'),
    ('ivory', '#FFFFF0'),
    ('khaki', '#F0E68C'),
    ('lavender', '#E6E6FA'),
    ('lavenderblush', '#FFF0F5'),
    ('lawngreen', '#7CFC00'),
    ('lemonchiffon', '#FFFACD'),
    ('lightblue', '#ADD8E6'),
    ('lightcoral', '#F08080'),
    ('lightcyan', '#E0FFFF'),
    ('lightgoldenrodyellow', '#FAFAD2'),
    ('lightgreen', '#90EE90'),
    ('lightgrey', '#D3D3D3'),
    ('lightpink', '#FFB6C1'),
    ('lightsalmon', '#FFA07A'),
    ('lightseagreen', '#20B2AA'),
    ('lightskyblue', '#87CEFA'),
    ('lightslategray', '#778899'),
    ('lightsteelblue', '#B0C4DE'),
    ('lightyellow', '#FFFFE0'),
    ('limegreen', '#32CD32'),
    ('linen', '#FAF0E6'),
    ('mediumaquamarine', '#66CDAA'),
    ('mediumblue', '#0000CD'),
    ('mediumorchid', '#BA55D3'),
    ('mediumpurple', '#9370DB'),
    ('mediumseagreen', '#3CB371'),
    ('mediumslateblue', '#7B68EE'),
    ('mediumspringgreen', '#00FA9A'),
    ('mediumturquoise', '#48D1CC'),
    ('mediumvioletred', '#C71585'),
    ('midnightblue', '#191970'),
    ('mintcream', '#F5FFFA'),
    ('mistyrose', '#FFE4E1'),
    ('moccasin', '#FFE4B5'),
    ('navajowhite', '#FFDEAD'),
    ('oldlace', '#FDF5E6'),
    ('olivedrab', '#6B8E23'),
    ('orange', '#FFA500'),
    ('orangered', '#FF4500'),
    ('orchid', '#DA70D6'),
    ('palegoldenrod', '#EEE8AA'),
    ('palegreen', '#98FB98'),
    ('paleturquoise', '#AFEEEE'),
    ('palevioletred', '#DB7093'),
    ('papayawhip', '#FFEFD5'),
    ('peachpuff', '#FFDAB9'),
    ('peru', '#CD853F'),
    ('pink', '#FFC0CB'),
    ('plum', '#DDA0DD'),
    ('powderblue', '#B0E0E6'),
    ('rosybrown', '#BC8F8F'),
    ('royalblue', '#4169E1'),
    ('saddlebrown', '#8B4513'),
    ('salmon', '#FA8072'),
    ('sandybrown', '#F4A460'),
    ('seagreen', '#2E8B57'),
    ('seashell', '#FFF5EE'),
    ('sienna', '#A0522D'),
    ('skyblue', '#87CEEB'),
    ('slateblue', '#6A5ACD'),
    ('slategray', '#708090'),
    ('snow', '#FFFAFA'),
    ('springgreen', '#00FF7F'),
    ('steelblue', '#4682B4'),
    ('tan', '#D2B48C'),
    ('thistle', '#D8BFD8'),
    ('tomato', '#FF6347'),
    ('turquoise', '#40E0D0'),
    ('violet', '#EE82EE'),
    ('wheat', '#F5DEB3'),
    ('whitesmoke', '#F5F5F5'),
    ('yellowgreen', '#9ACD32'),
    ]

# colortable
colortable = {}

for name, color in _colortable:
    colortable[name] = colorStringToDoubles(color)
