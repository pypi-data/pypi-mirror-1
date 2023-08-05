"""
Chimera's Pango-Cairo bindings
~~~~~~~~~~~~~~~~~~~~
A Simple API for doing Chimera layers using Pango with the Cairo
rendering backend

"""

__author__ = 'Benjamin Saller <bcsaller@objectrealms.net>'
__docformat__ = 'restructuredtext'
__copyright__ = 'Copyright ObjectRealms, LLC, 2005-2006'
__license__  = 'The GNU Public License V2+'


cdef class CairoSurface:
    pass

cdef class CairoContext:
    cdef cairo_t *context
    cdef CairoSurface surface
    cdef cairo.cairo_font_options_t *fo

#
# Cairo Name maps
#
cairo_operators = {
    'clear' : cairo.CAIRO_OPERATOR_CLEAR,
    'source' : cairo.CAIRO_OPERATOR_SOURCE,
    'over' : cairo.CAIRO_OPERATOR_OVER,
    'in' : cairo.CAIRO_OPERATOR_IN,
    'out': cairo.CAIRO_OPERATOR_OUT,
    'atop' : cairo.CAIRO_OPERATOR_ATOP,

    'dest' : cairo.CAIRO_OPERATOR_DEST,
    'dest_over':   cairo.CAIRO_OPERATOR_DEST_OVER,
    'dest_in' : cairo.CAIRO_OPERATOR_DEST_IN,
    'dest_out' : cairo.CAIRO_OPERATOR_DEST_OUT,
    'dest_atop': cairo.CAIRO_OPERATOR_DEST_ATOP,

    'xor' : cairo.CAIRO_OPERATOR_XOR,
    'add' : cairo.CAIRO_OPERATOR_ADD,
    'saturate' : cairo.CAIRO_OPERATOR_SATURATE
    }

cairo_antialias = {
    'default' : cairo.CAIRO_ANTIALIAS_DEFAULT,
    'none' :   cairo.CAIRO_ANTIALIAS_NONE,
    'grey' :   cairo.CAIRO_ANTIALIAS_GRAY,
    'gray' :   cairo.CAIRO_ANTIALIAS_GRAY,
    'subpixel': cairo.CAIRO_ANTIALIAS_SUBPIXEL
    }

cairo_fill_rule =  {
    'winding' : cairo.CAIRO_FILL_RULE_WINDING,
    'even_odd' : cairo.CAIRO_FILL_RULE_EVEN_ODD
    }

cairo_line_cap = {
    "butt" : cairo.CAIRO_LINE_CAP_BUTT,
    "round" : cairo.CAIRO_LINE_CAP_ROUND,
    "square" : cairo.CAIRO_LINE_CAP_SQUARE
    }

cairo_line_join = {
    'miter' : cairo.CAIRO_LINE_JOIN_MITER,
    'round' : cairo.CAIRO_LINE_JOIN_ROUND,
    'bevel' : cairo.CAIRO_LINE_JOIN_BEVEL
    }

# Type to map to common industry names
cairo_hint_style = {
    'default' : cairo.CAIRO_HINT_STYLE_DEFAULT,
    'none'  : cairo.CAIRO_HINT_STYLE_NONE,
    None : cairo.CAIRO_HINT_STYLE_NONE,
    'slight' : cairo.CAIRO_HINT_STYLE_SLIGHT,
    'medium' : cairo.CAIRO_HINT_STYLE_MEDIUM,
    'full' : cairo.CAIRO_HINT_STYLE_FULL,
    'strong' : cairo.CAIRO_HINT_STYLE_FULL
    }

cairo_hint_metrics = {
    'default' : cairo.CAIRO_HINT_METRICS_DEFAULT,
    'off' : cairo.CAIRO_HINT_METRICS_OFF,
    'on'  : cairo.CAIRO_HINT_METRICS_ON,
    False : cairo.CAIRO_HINT_METRICS_OFF,
    True : cairo.CAIRO_HINT_METRICS_ON,
    }

cairo_path_data = {
    cairo.CAIRO_PATH_MOVE_TO : 'move_to',
    cairo.CAIRO_PATH_LINE_TO : 'line_to',
    cairo.CAIRO_PATH_CURVE_TO : 'curve_to',
    cairo.CAIRO_PATH_CLOSE_PATH : 'close_path'
    }

cairo_slant =  {
    'normal' : cairo.CAIRO_FONT_SLANT_NORMAL,
    'italic' : cairo.CAIRO_FONT_SLANT_ITALIC,
    'oblique' : cairo.CAIRO_FONT_SLANT_OBLIQUE
    }

cairo_subpixel_order = {
    None : cairo.CAIRO_SUBPIXEL_ORDER_DEFAULT,
    'default' : cairo.CAIRO_SUBPIXEL_ORDER_DEFAULT,
    "rgb" : cairo.CAIRO_SUBPIXEL_ORDER_RGB,
    "brg" : cairo.CAIRO_SUBPIXEL_ORDER_BGR,
    "vrgb" : cairo.CAIRO_SUBPIXEL_ORDER_VRGB,
    "vbgr" : cairo.CAIRO_SUBPIXEL_ORDER_VBGR
    }

cairo_content = {
    'color' : cairo.CAIRO_CONTENT_COLOR,
    'alpha' : cairo.CAIRO_CONTENT_ALPHA,
    'color_alpha' : cairo.CAIRO_CONTENT_COLOR_ALPHA,
    'all' : cairo.CAIRO_CONTENT_COLOR_ALPHA,
    'both' : cairo.CAIRO_CONTENT_COLOR_ALPHA,
    }

cairo_format = {
    'argb' : cairo.CAIRO_FORMAT_ARGB32,
    'rgb'  : cairo.CAIRO_FORMAT_RGB24,
    'L'    : cairo.CAIRO_FORMAT_A8,
    'a8'    : cairo.CAIRO_FORMAT_A8,
    '1'    : cairo.CAIRO_FORMAT_A1,
    'a1'    : cairo.CAIRO_FORMAT_A1,
    }


cairo_extend = {
    None : cairo.CAIRO_EXTEND_NONE,
    'none' : cairo.CAIRO_EXTEND_NONE,
    'repeat' : cairo.CAIRO_EXTEND_REPEAT,
    'reflect' : cairo.CAIRO_EXTEND_REFLECT,
    }

cairo_filter = {
    'fast' : cairo.CAIRO_FILTER_FAST ,
    'good' : cairo.CAIRO_FILTER_GOOD ,
    'best' : cairo.CAIRO_FILTER_BEST ,
    'nearest' : cairo.CAIRO_FILTER_NEAREST ,
    'bilinear' : cairo.CAIRO_FILTER_BILINEAR ,
    'gaussian' : cairo.CAIRO_FILTER_GAUSSIAN
    }





