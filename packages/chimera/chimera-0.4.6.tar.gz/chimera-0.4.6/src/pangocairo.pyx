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


cimport libc
cimport glib
cimport python

cimport cairo
from cairo cimport cairo_matrix_t

cimport pango

from cStringIO import StringIO
import colors
import tempfile
import webbrowser
import os

PANGO_SCALE = 1024

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



#
# Pango Name maps
#

pango_underline = {
    'none' : pango.PANGO_UNDERLINE_NONE,
    None   : pango.PANGO_UNDERLINE_NONE,
    'single' : pango.PANGO_UNDERLINE_SINGLE,
    'double' : pango.PANGO_UNDERLINE_DOUBLE,
    'low'    : pango.PANGO_UNDERLINE_LOW,
    }

pango_style = {
    'normal' : pango.PANGO_STYLE_NORMAL,
    'oblique' : pango.PANGO_STYLE_OBLIQUE,
    'italic'  : pango.PANGO_STYLE_ITALIC
    }

pango_variant = {
    'normal' : pango.PANGO_VARIANT_NORMAL,
    'smallcap' : pango.PANGO_VARIANT_SMALL_CAPS,
    'smallcaps' : pango.PANGO_VARIANT_SMALL_CAPS,
    }

pango_weight = {
    'ultralight' : pango.PANGO_WEIGHT_ULTRALIGHT,
    'light' : pango.PANGO_WEIGHT_LIGHT,
    'normal': pango.PANGO_WEIGHT_NORMAL,
    'semibold' : pango.PANGO_WEIGHT_SEMIBOLD,
    'bold' : pango.PANGO_WEIGHT_BOLD,
    'ultrabold' : pango.PANGO_WEIGHT_ULTRABOLD,
    'heavy' : pango.PANGO_WEIGHT_HEAVY,
    }

pango_stretch = {
    'ultra_condensed' : pango.PANGO_STRETCH_ULTRA_CONDENSED,
    'extra_condensed' : pango.PANGO_STRETCH_EXTRA_CONDENSED,
    'condensed' : pango.PANGO_STRETCH_CONDENSED,
    'semi_condensed' : pango.PANGO_STRETCH_SEMI_CONDENSED,
    'normal' : pango.PANGO_STRETCH_NORMAL,
    'semi_expanded' : pango.PANGO_STRETCH_SEMI_EXPANDED,
    'expanded' : pango.PANGO_STRETCH_EXPANDED,
    'extra_expanded' : pango.PANGO_STRETCH_EXTRA_EXPANDED,
    'ultra_expanded' : pango.PANGO_STRETCH_ULTRA_EXPANDED
    }

pango_wrap = {
    'word' : pango.PANGO_WRAP_WORD,
    'char' : pango.PANGO_WRAP_CHAR,
    'wordchar' : pango.PANGO_WRAP_WORD_CHAR
    }

pango_alignment = {
    'left' : pango.PANGO_ALIGN_LEFT,
    'center' : pango.PANGO_ALIGN_CENTER,
    'right' : pango.PANGO_ALIGN_RIGHT
    }

pango_ellipsize = {
    'none' : pango.PANGO_ELLIPSIZE_NONE,
    None : pango.PANGO_ELLIPSIZE_NONE,
    'start' : pango.PANGO_ELLIPSIZE_START,
    'middle' : pango.PANGO_ELLIPSIZE_MIDDLE,
    'end' : pango.PANGO_ELLIPSIZE_END
    }

#
# Surface
#
# surface callbacks
cdef class  CairoContext

cdef cairo.cairo_status_t writePNG(void *closure, char *data, int length):
    cdef object cur
    cur = python.PyString_FromStringAndSize(data, length)
    (<object>closure).write(cur)
    return cairo.CAIRO_STATUS_SUCCESS

cdef cairo.cairo_status_t readPNG(void *closure, char *data, int
                                  length):
    res = (<object>closure).read(length)
    # now put the buffer data into the in/out arg, data
    libc.memcpy(data, python.PyString_AsString(res), length)
    return cairo.CAIRO_STATUS_SUCCESS


cdef class CairoMatrix:
    cdef cairo_matrix_t matrix

    def __init__(self, value=None):
        cairo.cairo_matrix_init_identity(&self.matrix)
        if isinstance(value, tuple) and len(value) == 6:
            cairo.cairo_matrix_init(&self.matrix,
                                    value[0],
                                    value[1],
                                    value[2],
                                    value[3],
                                    value[4],
                                    value[5])
        elif isinstance(value, CairoMatrix):
            self._fromMatrix(&(<CairoMatrix>(value)).matrix)

    cdef _fromMatrix(self, cairo.cairo_matrix_t *m):
        cairo.cairo_matrix_init(&self.matrix, m.xx, m.yx, m.xy, m.yy, m.x0, m.y0)

    cdef _asTuple(self, cairo.cairo_matrix_t *m):
        return (m.xx, m.yx, m.xy, m.yy, m.x0, m.y0)

    def asTuple(self):
        return self._asTuple(&self.matrix)

    def __repr__(self):
        return "<CairoMatrix %r>" % (self.asTuple(),)

    def __getitem__(self, index):
        t = self.asTuple()
        return t[index]

    def init_translate(self, tx, ty):
        cairo.cairo_matrix_init_translate(&self.matrix, tx, ty)
        return self

    def translate(self, tx, ty):
        cairo.cairo_matrix_translate(&self.matrix, tx, ty)
        return self

    def init_scale(self, sx, sy):
        cairo.cairo_matrix_init_scale(&self.matrix, sx, sy)
        return self

    def scale(self, sx, sy):
        cairo.cairo_matrix_scale(&self.matrix, sx, sy)
        return self

    def init_rotate(self, radians):
        cairo.cairo_matrix_init_rotate(&self.matrix, radians)
        return self

    def rotate(self, radians):
        cairo.cairo_matrix_rotate(&self.matrix, radians)
        return self

    def init_rotateDegrees(self, degrees):
        radians = degrees / 57.2957795
        cairo.cairo_matrix_init_rotate(&self.matrix, radians)
        return self

    def rotateDegrees(self, degrees):
        radians = degrees / 57.2957795
        return self.rotate(radians)

    def invert(self):
        cairo.cairo_matrix_invert(&self.matrix)
        return self

    def multiply(self, CairoMatrix other):
        cdef cairo.cairo_matrix_t m
        cairo.cairo_matrix_multiply(&m, &(self.matrix), &other.matrix)
        return CairoMatrix(self._asTuple(&m))

##     def __mul__(self, CairoMatrix other):
##         cdef cairo.cairo_matrix_t m
##         cairo.cairo_matrix_multiply(&m, &self.matrix, &other.matrix)
##         return CairoMatrix(self._asTuple(&m))


    def transform_distance(self, x, y):
        cdef double dx, dy
        dx = x
        dy = y
        cairo.cairo_matrix_transform_distance(&self.matrix,
                                              &dx, &dy)

        return (dx, dy)

    def transform_point(self, x, y):
        cdef double dx, dy
        dx = x
        dy = y
        cairo.cairo_matrix_transform_point(&self.matrix,
                                           &dx, &dy)

        return (dx, dy)



cdef class CairoSurface:
    cdef cairo.cairo_surface_t *surface


    def __dealloc__(self):
        cairo.cairo_surface_destroy(self.surface)

    def finish(self):
        cairo.cairo_surface_finish(self.surface)

    def flush(self):
        cairo.cairo_surface_flush(self.surface)


    def writePng(self, filename):
        cdef cairo.cairo_status_t status
        status = cairo.cairo_surface_write_to_png(self.surface,
                                                  filename)
        if status != cairo.CAIRO_STATUS_SUCCESS:
            raise IOError(cairo.cairo_status_to_string(status))
        return status

    def asFile(self):
        # return the as a PNG byte stream
        cdef cairo.cairo_status_t status
        output = StringIO()
        status = cairo.cairo_surface_write_to_png_stream(self.surface,
                                                         <cairo.cairo_write_func_t>writePNG,
                                                         <void *>output)
        output.seek(0)
        return output


    def asPngBuffer(self):
        return self.asFile().getvalue()

    def __str__(self):
        return self.asPngBuffer()

    def show(self):
        """Convenience method to display the image in its current
        state"""
        cairo.cairo_surface_flush(self.surface)
        fd, pn = tempfile.mkstemp('.png')
        self.writePng(pn)
        os.fsync(fd)
        webbrowser.open("file://%s" % pn)
        os.close(fd)
        os.remove(pn)

    def Context(self):
        return CairoContext(self)


cdef class ImageSurface(CairoSurface):
    def __init__(self, *args):
        if len(args) == 3:
            self.create(args[0], args[1], args[2])
            self.clear()
        elif len(args) == 1:
            if hasattr(args[0], 'read'):
                self.fromPngBuffer(args[0])
            else:
                self.fromPng(args[0])

    def create_similar(self, content=None, width=None, height=None):
        """Create an image mostly like this one"""
        cdef cairo.cairo_surface_t *other_surface
        cdef ImageSurface img

        if content is None: content = cairo_content['color_alpha']
        if isinstance(content, basestring): content = cairo_content[content]

        width = width or self.width
        height = height or self.height

        other_surface = cairo.cairo_surface_create_similar(self.surface,
                                                           content,
                                                           width,
                                                           height)
        img = ImageSurface()
        img.surface = other_surface
        img.clear()
        return img

    def clone(self):
        """create a direct copy of this image with its content"""
        size = self.size
        img = self.create_similar("color_alpha", *size)
        c = img.Context()
        c.paint(self)
        return img


    cdef clear(self):
        cdef CairoContext c
        c = CairoContext(self)

        # transparent fill the surface
        # this works around an issue where the default
        # operator doesn't always create a clean
        # transparent surface for us
        cairo.cairo_rectangle(c.context, 0, 0,
                              self.width,
                              self.height)
        cairo.cairo_set_source_rgba(c.context, 0.0, 0.0, 0.0, 0.0)
        cairo.cairo_set_operator(c.context, cairo.CAIRO_OPERATOR_CLEAR)
        cairo.cairo_fill(c.context)
        cairo.cairo_surface_flush(self.surface)


    cdef create(self, format, width, height):
        if isinstance(format, basestring):
            format = cairo_format[format]
        self.surface = cairo.cairo_image_surface_create(format,
                                                        width,
                                                        height)
    cdef fromPng(self, filename):
        self.surface = cairo.cairo_image_surface_create_from_png(filename)

    cdef fromPngBuffer(self, buffer):
        self.surface = cairo.cairo_image_surface_create_from_png_stream(readPNG,
                                                                        <void *>buffer)

    property width:
        def __get__(self):
            return cairo.cairo_image_surface_get_width(self.surface)

    property height:
        def __get__(self):
            return cairo.cairo_image_surface_get_height(self.surface)

    property size:
        def __get__(self):
            return self.width, self.height

    def __repr__(self):
        return "<ImageSurface %sx%s>" %(self.width,
                                        self.height)


cdef class CairoPattern:
    # Abstract Pattern class
    cdef cairo.cairo_pattern_t *_pattern

    def __dealloc__(self):
        cairo.cairo_pattern_destroy(self._pattern)

    property status:
        def __get__(self):
            return cairo.cairo_pattern_status(self._pattern)

    def set(self, CairoContext c):
        cairo.cairo_set_source(c.context, self._pattern)

    property matrix:
        def __get__(self):
            cdef CairoMatrix m
            cdef cairo.cairo_matrix_t _mat
            m = CairoMatrix()
            cairo.cairo_pattern_get_matrix(self._pattern, &_mat)
            m._fromMatrix(&_mat)
            return m

        def __set__(self, CairoMatrix value):
            cairo.cairo_pattern_set_matrix(self._pattern, &(value.matrix))


    def identity(self):
        self.matrix = self.matrix.identity()

    def scale(self, double sx, double sy):
        self.matrix = self.matrix.scale(sx, sy)

    def translate(self, double tx, double ty):
        self.matrix = self.matrix.translate(tx, ty)

    def rotate(self, radians):
        self.matrix = self.matrix.rotate(radians)

    def rotateDegrees(self, degrees):
        radians = degrees / 57.2957795
        self.rotate(radians)

cdef class SolidPattern(CairoPattern):
    def __init__(self, color, alpha=1.0):
        r, g, b, a = colors.parseColorToRGBA(color, masterAlpha=alpha)
        self._pattern = cairo.cairo_pattern_create_rgba(r, g, b, a)


cdef class SurfacePattern(CairoPattern):
    def __init__(self, CairoSurface s):
        self._pattern = cairo.cairo_pattern_create_for_surface(s.surface)

    property extend:
        def __get__(self):
            return cairo.cairo_pattern_get_extend(self._pattern)
        def __set__(self, value):
            if isinstance(value, (basestring, type(None))):
                value = cairo_extend[value]
            cairo.cairo_pattern_set_extend(self._pattern, value)

    property filter:
        def __get__(self):
            return cairo.cairo_pattern_get_filter(self._pattern)
        def __set__(self, value):
            if isinstance(value, basestring):
                value = cairo_filter[value]
            cairo.cairo_pattern_set_filter(self._pattern, value)

    def set(self, CairoContext c, x=0, y=0):
        cdef cairo.cairo_matrix_t matrix
        if x or y:
            cairo.cairo_matrix_init_translate(&matrix, -x, -y)
            cairo.cairo_pattern_set_matrix(self._pattern, &matrix)
        cairo.cairo_set_source(c.context, self._pattern)


cdef class _Gradient(CairoPattern):
    def add_color_stop(self, double offset, color):
        r, g, b, a = colors.parseColorToRGBA(color)
        cairo.cairo_pattern_add_color_stop_rgba(self._pattern, offset,
                                                r, g, b, a)

cdef class LinearGradient(_Gradient):
    def __init__(self, double x0, double y0, double x1, double y1):
        self._pattern = cairo.cairo_pattern_create_linear(x0, y0,
                                                          x1, y1)

cdef class RadialGradient(_Gradient):
    def __init__(self, double cx0, double cy0, double radius0,
                 double cx1, double cy1, radius1):
        self._pattern = cairo.cairo_pattern_create_radial(cx0, cy0, radius0,
                                                          cx1, cy1, radius1)




cdef class Rect:
    cdef pango.PangoRectangle r

    def __init__(self, x=0, y=0, width=0, height=0):
        self.r.x = x
        self.r.y = y
        self.r.width = width
        self.r.height = height

    property x:
        def __get__(self): return self.r.x
        def __set__(self, value): self.r.x = value
    property y:
        def __get__(self): return self.r.y
        def __set__(self, value): self.r.y = value
    property width:
        def __get__(self): return self.r.width
        def __set__(self, value): self.r.width = value
    property height:
        def __get__(self): return self.r.height
        def __set__(self, value): self.r.height = value

    def __add__(self, other):
        # return a Rect (I know, a different type)
        # containing the dimensions of both
        x = min(self.x, other.x)
        y = min(self.y, other.y)
        w = max(self.x + self.width,
                other.x + other.width) -x
        h = max(self.y + self.height,
                other.y + other.height) - y
        return Rect(x, y, w, h)

    def __repr__(self):
        return "<Rect (%s,%s):(%s x %s)>" %(self.x, self.y,
                                            self.width, self.height)


cdef class PangoLayout

cdef class PangoText:
    cdef pango.PangoAttrList *attrs
    cdef PangoLayout layout
    cdef pango.PangoFontDescription *desc
    cdef object _text

    def __init__(self, text):
        self._text = text
        self.setLayout(None)

    def setLayout(self, PangoLayout layout):
        if self.attrs != NULL:
            pango.pango_attr_list_unref(self.attrs)

        self.layout = layout
        self.attrs = pango.pango_attr_list_new()

    def __dealloc__(self):
        self.layout = None
        if self.attrs != NULL:
            pango.pango_attr_list_unref(self.attrs)

    cdef applyAttribute(self, pango.PangoAttribute *attr):
        attr.start_index = 0
        attr.end_index = len(self.text)
        pango.pango_attr_list_insert(self.attrs, attr)

    property text:
        def __get__(self):
            return self._text
        def __set__(self, value):
            self._text = value

    property font:

        def __set__(self, value):
            cdef pango.PangoFontDescription *font
            cdef char *desc
            font = pango.pango_font_description_from_string(value)
            if font != NULL:
                self.applyAttribute(pango.pango_attr_font_desc_new(font))
                # the attr seems to just use the ref directly, we can't
                # free it, the list destroy will have to
                # XXX: but the code doesn't show this....
                #glib.g_object_unref(font)

    property foreground:
        def __set__(self, value):
            r,g,b = colors.parseColorToRGBA(value)[:3]
            self.applyAttribute(pango.pango_attr_foreground_new(r, g, b))

    property background:
        def __set__(self, value):
            r,g,b = colors.parseColorToRGBA(value)[:3]
            self.applyAttribute(pango.pango_attr_background_new(r, g, b))

    property size:
        def __set__(self, int value):
            value = value * PANGO_SCALE
            self.applyAttribute(pango.pango_attr_size_new(value))

    property style:
        def __set__(self, value):
            if isinstance(value, basestring):
                value = pango_style[value]
            self.applyAttribute(pango.pango_attr_style_new(value))

    property weight:
        def __set__(self, value):
            if isinstance(value, basestring):
                value = pango_weight[value]
            self.applyAttribute(pango.pango_attr_weight_new(value))

    property variant:
        def __set__(self, value):
            if isinstance(value, basestring):
                value = pango_variant[value]
            self.applyAttribute(pango.pango_attr_variant_new(value))

    property stretch:
        def __set__(self, value):
            if isinstance(value, basestring):
                value = pango_stretch[value]
            self.applyAttribute(pango.pango_attr_stretch_new(value))

    property underline:
        def __set__(self, value):
            if isinstance(value, (basestring, type(None))):
                value = pango_underline[value]
            self.applyAttribute(pango.pango_attr_underline_new(value))

    property underline_color:
        def __set__(self, value):
            r,g,b = color.parseColorToRGBA(value)[:3]
            self.applyAttribute(pango.pango_attr_underline_color_new(r, g, b))

    property strikethrough:
        def __set__(self, value):
            if isinstance(value, basestring):
                value = pango_strikethrough[value]
            self.applyAttribute(pango.pango_attr_strikethrough_new(value))

    property strikethrough_color:
        def __set__(self, value):
            r,g,b = color.parseColorToRGBA(value)[:3]
            self.applyAttribute(pango.pango_attr_strikethrough_color_new(r, g, b))

    property rise:
        def __set__(self, int value):
            self.applyAttribute(pango.pango_attr_rise_new(value))

    property scale:
        def __set__(self, double value):
            self.applyAttribute(pango.pango_attr_scale_new(value))

    property fallback:
        def __set__(self, value):
            self.applyAttribute(pango.pango_attr_fallback_new(value))

    property letter_spacing:
        def __set__(self, int value):
            self.applyAttribute(pango.pango_attr_letter_spacing_new(value))


    def __repr__(self):
        return "<PangoText %r>" % (self.text)


cdef class PangoLayout:
    """Attributes set on the layout apply to the entire layout by
    default. Attributed sections of text can override the layouts
    properties.
    """
    cdef CairoContext context
    cdef pango.PangoLayout *_layout
    cdef pango.PangoContext *_pango
    cdef pango.PangoCairoFontMap *_fontmap
    cdef pango.PangoAttrList *attrs
    cdef cairo.cairo_font_options_t *fo

    cdef object _texts
    cdef int _updated
    
    def __init__(self):
        cdef pango.PangoCairoFontMap *fontmap
        cdef pango.PangoContext *_pango

        self._texts = []
        self.updated = True

        self.fo = cairo.cairo_font_options_create()
        self._fontmap = <pango.PangoCairoFontMap*>pango.pango_cairo_font_map_get_default()

        self._pango  = pango.pango_cairo_font_map_create_context(self._fontmap)
        self._layout  = pango.pango_layout_new(self._pango)

        self.attrs = pango.pango_attr_list_new()
        pango.pango_layout_set_attributes(self._layout, self.attrs)


    def __dealloc__(self):
        self.context = None
        cairo.cairo_font_options_destroy(self.fo)
        pango.pango_attr_list_unref(self.attrs)
        glib.g_object_unref(self._layout)
        glib.g_object_unref(self._pango)


    def getContext(self):
        return self.context

    def setContext(self, CairoContext context):
        # move a layout from one context to another
        self.context = context
        # static defaults
        self.antialias = "subpixel"
        self.update()

    def surfaceFor(self, w=None, h=None):
        # return a surface that should contain the layout
        # XXX: control over surface class, to support SVG and others
        size = self.size
        size = w or size[0], h or size[1]
        return ImageSurface("argb", *size)

    def contextFor(self, w=None, h=None, ctm=False):
        """Create an image sized to this layout,
        bind this layout to it and return a new cairo context
        """
        size = self.size
        w, h = w or size[0], h or size[1]
        if ctm and self.context:
            rect = self.context.bounds
            w = rect.width
            h = rect.height
        if self.context:
            im = self.context.image.create_similar("color_alpha", w, h)
        else:
            im = self.surfaceFor(w, h)

        c = CairoContext(im)
        if ctm and self.context:
            c.matrix = self.context.matrix
        self.setContext(c)
        return c

    property antialias:
        def __set__(self, value):
            if isinstance(value, basestring):
                value = cairo_antialias[value]
            cairo.cairo_set_antialias(self.context.context, value)
            pango.pango_cairo_update_context(self.context.context, self._pango)

    property hint_style:
        def __set__(self, value):
            if isinstance(value, (basestring, type(None))):
                value = cairo_hint_style[value]
            cairo.cairo_font_options_set_hint_style(self.fo, value)
            pango.pango_cairo_update_context(self.context.context, self._pango)

    property hint_metrics:
        def __set__(self, value):
            if isinstance(value, (basestring, bool)):
                value = cairo_hint_metrics[value]
            cairo.cairo_font_options_set_hint_metrics(self.fo, value)
            pango.pango_cairo_update_context(self.context.context, self._pango)

    property resolution:
        def __get__(self):
            return pango.pango_cairo_context_get_resolution(self._pango)
        def __set__(self, value):
            pango.pango_cairo_context_set_resolution(self._pango, value)
            pango.pango_cairo_update_context(self.context.context, self._pango)


    property width:
        def __get__(self):
            return pango.pango_layout_get_width(self._layout) / PANGO_SCALE
        def __set__(self, value):
            value = value * PANGO_SCALE
            pango.pango_layout_set_width(self._layout, value)

    def __add__(self, value):
        # Its const which may create problems down the road
        # for pyrex
        if not isinstance(value, PangoText):
            value = PangoText(value)
        # Establish that text belongs to this
        # layout instance
        value.setLayout(self)
        self.texts.append(value)
        self.updated = False
        return self

    property updated:
        # internal use, kinda a pyrex hack
        def __get__(self): return self._updated
        def __set__(self, value): self._updated = bool(value)
        
    property texts:
        def __get__(self):
            return self._texts

    property text:
        def __get__(self):
            cdef char *t
            # we do not compose, but we should
            # update right now would be recursive but
            # it could just call this method...
            t = pango.pango_layout_get_text(self._layout)
            if t == NULL:
                t = ""
            text = t
            return text

        def __set__(self, value):
            if isinstance(value, unicode):
                value = value.encode("utf-8")
            value = value.rstrip()
            pango.pango_layout_set_text(self._layout, value, -1)


    property font:
        # Change the default font for the layout
        def __get__(self):
            cdef pango.PangoFontDescription *font
            cdef char *desc
            font = pango.pango_layout_get_font_description(self._layout)
            if font != NULL:
                desc = pango.pango_font_description_to_string(font)
                if desc != NULL:
                    pydesc  = desc
                    glib.g_free(desc)
                    return pydesc
            return '<system default>'

        def __set__(self, value):
            cdef pango.PangoFontDescription *font
            font = pango.pango_font_description_from_string(value)
            pango.pango_layout_set_font_description(self._layout, font)
            #glib.g_free(font)

    property wrap:
        def __set__(self, value):
            if isinstance(value, basestring):
                value = pango_wrap[value]
            pango.pango_layout_set_wrap(self._layout, value)

    property indent:
        def __set__(self, int value):
            pango.pango_layout_set_indent(self._layout, value)

    property spacing:
        def __set__(self, int value):
            pango.pango_layout_set_spacing(self._layout, value)

    property justify:
        def __set__(self, int value):
            pango.pango_layout_set_justify(self._layout, value)

    property auto_dir:
        def __set__(self, int value):
            pango.pango_layout_set_auto_dir(self._layout, value)

    property alignment:
        def __set__(self, value):
            if isinstance(value, basestring):
                value = pango_alignment[value]
            pango.pango_layout_set_alignment(self._layout, value)

    property single_paragraph:
        def __set__(self, value):
            pango.pango_layout_set_single_paragraph_mode(self._layout,
                                                         value)
    property ellipsize:
        def __set__(self, value):
            if isinstance(value, (basestring, type(None))):
                value = pango_ellipsize[value]
            pango.pango_layout_set_ellipsize(self._layout, value)

    property size:
        def __get__(self):
            cdef pango.PangoRectangle ink, logical
            if not self.updated: self.update()
            pango.pango_layout_get_pixel_extents(self._layout,
                                                 &ink,
                                                 &logical)
            return (logical.width, logical.height)

    property line_count:
        def __get__(self):
            return pango.pango_layout_get_line_count(self._layout)

    def update(self):
        cdef pango.PangoAttrIterator *aiter
        cdef pango.PangoAttribute *attr
        cdef glib.GSList *attrs
        cdef glib.GSList *l
        cdef char *t

        cdef double x, y
        cdef Rect ink, logical

        # First process all the texts setting the ranges and the attrs
        # as needed, then we update the rendering context
        start = 0
        for value in self.texts:
            text = self.text
            start = len(text)
            end   =  start + len(value.text)

            # append its text and its attributes
            # iter all attributes
            # setting its start index to range
            # so that the text sections are attribute
            # independent by default
            aiter = pango.pango_attr_list_get_iterator((<PangoText>value).attrs)
            attrs = pango.pango_attr_iterator_get_attrs(aiter)
            l = attrs

            self.text = text + value.text
            while l:
                attr = <pango.PangoAttribute*> l.data
                attr.start_index = start
                attr.end_index = end
                pango.pango_attr_list_insert(self.attrs, attr)
                l = l.next

            glib.g_slist_free(attrs)
            pango.pango_attr_iterator_destroy(aiter)


        pango.pango_cairo_context_set_font_options(self._pango,
                                                   self.fo)

        pango.pango_cairo_update_layout(self.context.context,
                                        self._layout)

        cairo.cairo_get_current_point(self.context.context,
                                      &x, &y)
        ink = Rect()
        logical = Rect()
        pango.pango_layout_get_pixel_extents(self._layout,
                                             &(ink.r),
                                             &(logical.r))
        logical.x = x
        logical.y = y
        ink.x = x
        ink.y = y


        # clear self.texts after each update
        # all the Text segments are consumed in self.text
        if self._texts:
            self._texts = []
        self._updated = True

        return logical

    def stroke(self, source, **kwargs):
        ext = self.update()
        pango.pango_cairo_layout_path(self.context.context,
                                      self._layout)

        if kwargs.get('preserve', False):
            self.context.stroke_preserve(source, **kwargs)
        else:
            self.context.stroke(source, **kwargs)
        return ext

    def fill(self, source, **kwargs):
        ext = self.update()
        pango.pango_cairo_layout_path(self.context.context,
                                      self._layout)

        if kwargs.get('preserve', False):
            self.context.fill_preserve(source, **kwargs)
        else:
            self.context.fill(source, **kwargs)
        return ext

    def show(self):
        ext = self.update()
        pango.pango_cairo_show_layout(self.context.context,
                                      self._layout)
        return ext


    def Text(self, text, fontspec=None):
        """Create a text span bound to this layout"""
        t = PangoText(text)
        # the ordering here is tricky, we need to set the layout and
        # apply attrs before update is called at which chance our
        # opportunity is lost.
        # set layout, add to text, add attr,
        # were this would need to be a full kwargs set
        t.setLayout(self)
        self + t
        if fontspec: t.font = fontspec
        return t

    def listFontFamilies(self):
        cdef pango.PangoFontFamily **fams
        cdef pango.PangoFontFace   **faces
        cdef int ct, i, j, fct

        pango.pango_context_list_families(self._pango,
                                          &fams,
                                          &ct)
        results = {}
        for i from 0 <= i < ct:
            l = results.setdefault(pango.pango_font_family_get_name(fams[i]), [])
            pango.pango_font_family_list_faces(fams[i], &faces, &fct)
            for j from 0 <= j < fct:
                l.append(pango.pango_font_face_get_face_name(faces[j]))

            l.sort(_casecmp)
            glib.g_free(faces)

        glib.g_free(fams)
        return results



def _casecmp(x, y):
    return cmp(x.lower(), y.lower())


cdef class CairoContext:
    cdef cairo.cairo_t *context
    cdef CairoSurface surface


    cdef double masterAlpha

    def __init__(self, CairoSurface surface):
        self.context = cairo.cairo_create(surface.surface)
        self.surface = surface
        self.alpha = 1.0

    def __dealloc__(self):
        if self.context != NULL:
            cairo.cairo_destroy(self.context)

    property image:
        def __get__(self):
            return self.surface

    property current_point:
        def __get__(self):
            cdef double x, y
            cairo.cairo_get_current_point(self.context, &x, &y)
            return (x,y)
        def __set__(self, point): self.move_to(*point)
            
    property alpha:
        def __get__(self):
            return self.masterAlpha
        def __set__(self, value):
            if isinstance(value, int):
                if value > 1:
                    value = value / 255.0
            self.masterAlpha = value

    property linewidth:
        def __get__(self):
            return cairo.cairo_get_line_width(self.context)
        def __set__(self, value):
            cairo.cairo_set_line_width(self.context, float(value))


    def save(self):
        cairo.cairo_save(self.context)

    def restore(self):
        cairo.cairo_restore(self.context)

    def write(self, filename):
        cdef cairo.cairo_status_t status
        status = self.surface.writePng(filename)
        if status != cairo.CAIRO_STATUS_SUCCESS:
            raise IOError(cairo.cairo_status_to_string(status))

    def asPngBuffer(self):
        return self.surface.asPngBuffer()


    def new_path(self):
        cairo.cairo_new_path(self.context)

    def rectangle(self, *args):
        if len(args) == 2:
            x, y = args[0][0], args[0][1]
            w,h  = args[1][0], args[1][1]
        elif len(args) == 4:
            x,y,w,h = args
        else:
            # its a Rect
            r = args[0]
            x,y,w,h = r.x, r.y, r.width, r.height

        cairo.cairo_rectangle(self.context, x,y,w,h)

    def clip(self):
        cairo.cairo_clip(self.context)

    def clip_preserve(self):
        cairo.cairo_clip_preserve(self.context)

    def clip_reset(self):
        cairo.cairo_reset_clip(self.context)


    def paint(self, source, **options):
        self.handle_source(source, options)
        cairo.cairo_paint_with_alpha(self.context,
                                     options.get("alpha", 1.0))

    def mask(self, source, **options):
        cdef CairoPattern pattern
        pattern  = self.handle_source(source, options)
        cairo.cairo_mask(self.context, pattern._pattern)

    def mask_surface(self, CairoSurface surface, **options):
        x = options.get('x', 0.0)
        y = options.get('y', 0.0)
        cairo.cairo_mask_surface(self.context, surface.surface, x, y)

    def fill(self, source, **options):
        self.handle_source(source, options)
        cairo.cairo_fill(self.context)

    def fill_preserve(self, source, **options):
        self.handle_source(source, options)
        cairo.cairo_fill_preserve(self.context)

    def stroke(self, source, **options):
        self.handle_source(source, options)
        cairo.cairo_stroke(self.context)

    def stroke_preserve(self, source, **options):
        self.handle_source(source, options)
        cairo.cairo_stroke_preserve(self.context)


    def handle_source(self, source, options):
        # This is a convenience method that will attempt to
        # set the CairoContext source from a variety of objects
        cdef CairoPattern pattern
        if isinstance(source, CairoPattern):
            pattern = source
            pattern.set(self)
        elif isinstance(source, CairoSurface):
            x = options.get("x", 0.0)
            y = options.get("y", 0.0)
            pattern  = SurfacePattern(<CairoSurface>source)
            pattern.set(self, x,y)
        elif isinstance(source, CairoContext):
            x = options.get("x", 0.0)
            y = options.get("y", 0.0)
            pattern  = SurfacePattern((<CairoContext>source).surface)
            pattern.set(self, x,y)
        elif isinstance(source, (basestring, tuple)):
            alpha = options.get("alpha", self.alpha)
            pattern = SolidPattern(source, alpha)
            pattern.set(self)
        elif hasattr(source, 'image') and isinstance(source.image, CairoSurface):
            # Should be a Chimera Image wrapper
            pattern  = SurfacePattern(<CairoSurface>source.image)
            pattern.set(self, x,y)
        else:
            pattern  = CairoPattern()
            pattern._pattern = cairo.cairo_get_source(self.context)

        return pattern

    def identity(self):
        """Reset the CTM"""
        cairo.cairo_identity_matrix(self.context)

    def transform(self, CairoMatrix m):
        cairo.cairo_transform(self.context, &m.matrix)

    def translate(self, double dx, double dy):
        cairo.cairo_translate(self.context, dx, dy)

    def scale(self, double sx, double sy):
        cairo.cairo_scale(self.context, sx, sy)

    def rotate(self, float radians):
        cairo.cairo_rotate(self.context, radians)

    def rotateDegrees(self, float degrees):
        radians = degrees / 57.2957795
        cairo.cairo_rotate(self.context, radians)

    property matrix:
        def __get__(self):
            cdef CairoMatrix m
            m = CairoMatrix()
            cairo.cairo_get_matrix(self.context, &m.matrix)
            return m

        def __set__(self,value):
            cdef CairoMatrix m
            m = CairoMatrix(value)
            cairo.cairo_set_matrix(self.context, &m.matrix)

    property font_matrix:
        def __get__(self):
            cdef CairoMatrix m
            m = CairoMatrix()
            cairo.cairo_get_font_matrix(self.context, &m.matrix)
            return m

        def __set__(self,value):
            cdef CairoMatrix m
            m = CairoMatrix(value)
            cairo.cairo_set_font_matrix(self.context, &m.matrix)


    def move_to(self, x, y):
        cairo.cairo_move_to(self.context, x, y)

    def line_to(self, double x, double y):
        cairo.cairo_line_to(self.context, x, y)

    def curve_to(self,
                 double x1, double y1,
                 double x2, double y2,
                 double x3, double y3):
        cairo.cairo_curve_to(self.context,
                                 x1, y1, x2, y2, x3, y3)

    def arc(self, double xc, double yc,
            double radius, double angle1, double angle2):
        cairo.cairo_arc(self.context, xc, yc, radius, angle1, angle2)

    def arc_negative(self, double xc, double yc,
                     double radius, double angle1, double angle2):
        cairo.cairo_arc_negative(self.context,
                                xc, yc, radius, angle1, angle2)


    def rel_move_to(self, dx, dy):
        cairo.cairo_rel_move_to(self.context, dx, dy)

    def rel_line_to(self, double dx, double dy):
        cairo.cairo_rel_line_to(self.context, dx, dy)

    def rel_curve_to(self,
                     double dx1, double dy1,
                     double dx2, double dy2,
                     double dx3, double dy3):
        cairo.cairo_rel_curve_to(self.context,
                                 dx1, dy1, dx2, dy2, dx3, dy3)

    def close_path(self):
        cairo.cairo_close_path(self.context)


    property operator:
        def __get__(self):
            return cairo.cairo_get_operator(self.context)
        def __set__(self, value):
            if isinstance(value, basestring):
                value = cairo_operators[value]
            cairo.cairo_set_operator(self.context, value)

    def Text(self, text, fontspec=None):
        t = PangoText(text)
        if fontspec: t.font = fontspec
        return t


    def Layout(self, text=None, fontspec=None):
        layout = PangoLayout()
        layout.setContext(self)
        return layout


    property bounds:
        def __get__(self):
            """return a bounding box (Rect) for the target surface
            after the Current Transformation Matrix (CTM) has been
            applied
            """

            w, h = self.image.size
            cords = []
            matrix = self.matrix
            for x, y in ((0,0), (w, 0), (w, h), (0, h)):
                cords.append(list(matrix.transform_point(x,y)))

            # top-left and bottom-right
            lt = cords[0]
            br = cords[0]
            for x, y in cords[1:]:
                if lt[0] > x: lt[0] = x
                if lt[1] > y: lt[1] = y
                if br[0] < x: br[0] = x
                if br[1] < y: br[1] = y
            return Rect(0, 0,
                        int(br[0] - lt[0]),
                        int(br[1] - lt[0])
                        )

