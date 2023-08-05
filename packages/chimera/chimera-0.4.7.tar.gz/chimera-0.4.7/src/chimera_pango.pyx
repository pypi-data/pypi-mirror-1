"""
chimera_pango
~~~~~~~~~~~~~~~~~~~~
render unicode text into chimera layers using pango and fontconfig

"""

__author__ = 'Benjamin Saller <bcsaller@objectrealms.net>'
__docformat__ = 'restructuredtext'
__copyright__ = 'Copyright ObjectRealms, LLC. 2005.'
__license__  = 'GPL Version 2+'

include "chimera_png.pyx"
include "chimera_svg.pyx"

PANGO_SCALE = 1024

cdef extern from "pango/pango.h":
     #
     # Extents
     #
     ctypedef struct PangoRectangle:
          int width
          int height

     #
     # Language
     #
     ctypedef struct PangoLanguage
     PangoLanguage *pango_language_from_string (char *language)

     #
     # Font
     #
     ctypedef enum PangoDirection:
          PANGO_DIRECTION_LTR,
          PANGO_DIRECTION_RTL,
          PANGO_DIRECTION_TTB_LTR,
          PANGO_DIRECTION_TTB_RTL,
          PANGO_DIRECTION_WEAK_LTR,
          PANGO_DIRECTION_WEAK_RTL,
          PANGO_DIRECTION_NEUTRAL

     ctypedef enum PangoStyle:
          PANGO_STYLE_NORMAL,
          PANGO_STYLE_OBLIQUE,
          PANGO_STYLE_ITALIC

     ctypedef enum PangoVariant:
          PANGO_VARIANT_NORMAL,
          PANGO_VARIANT_SMALL_CAPS

     ctypedef enum PangoWeight:
          PANGO_WEIGHT_ULTRALIGHT = 200,
          PANGO_WEIGHT_LIGHT = 300,
          PANGO_WEIGHT_NORMAL = 400,
          PANGO_WEIGHT_SEMIBOLD = 600,
          PANGO_WEIGHT_BOLD = 700,
          PANGO_WEIGHT_ULTRABOLD = 800,
          PANGO_WEIGHT_HEAVY = 900

     ctypedef enum PangoStretch:
          PANGO_STRETCH_ULTRA_CONDENSED,
          PANGO_STRETCH_EXTRA_CONDENSED,
          PANGO_STRETCH_CONDENSED,
          PANGO_STRETCH_SEMI_CONDENSED,
          PANGO_STRETCH_NORMAL,
          PANGO_STRETCH_SEMI_EXPANDED,
          PANGO_STRETCH_EXPANDED,
          PANGO_STRETCH_EXTRA_EXPANDED,
          PANGO_STRETCH_ULTRA_EXPANDED

     ctypedef enum PangoFontMask:
          PANGO_FONT_MASK_FAMILY  = 1 << 0,
          PANGO_FONT_MASK_STYLE   = 1 << 1,
          PANGO_FONT_MASK_VARIANT = 1 << 2,
          PANGO_FONT_MASK_WEIGHT  = 1 << 3,
          PANGO_FONT_MASK_STRETCH = 1 << 4,
          PANGO_FONT_MASK_SIZE    = 1 << 5



     ctypedef struct PangoFont
     ctypedef struct PangoFontDescription
     ctypedef struct PangoFontMetrics
     ctypedef struct PangoFontset
     ctypedef struct PangoFontFamily

     char * pango_font_family_get_name(PangoFontFamily *family)

     PangoFontDescription *pango_font_description_new()
     PangoFontDescription *pango_font_description_from_string (char
                                                               *str)
     char *pango_font_description_to_string (PangoFontDescription *fd)

     void pango_font_description_free (PangoFontDescription *desc)
     void pango_font_description_set_family (PangoFontDescription *desc, char*family)
     void pango_font_description_set_style (PangoFontDescription *desc,
                                            PangoStyle style)
     void pango_font_description_set_variant (PangoFontDescription *desc,
                                              PangoVariant variant)
     void pango_font_description_set_weight (PangoFontDescription *desc,
                                             PangoWeight weight)
     void pango_font_description_set_stretch (PangoFontDescription *desc,
                                              PangoStretch stretch)
     void pango_font_description_set_size (PangoFontDescription *desc,
                                           int                  size)
     void pango_font_description_set_absolute_size (PangoFontDescription *desc,
                                                    double size)
     #
     # FontMap
     #
     ctypedef struct PangoFontMap

     #
     # Context
     #
     ctypedef struct PangoContext
     PangoFontMap *pango_context_get_font_map(PangoContext *context)
     PangoFont *pango_context_load_font(PangoContext *context,
                                        PangoFontDescription *desc)

     void pango_context_list_families (PangoContext *context,
                                       PangoFontFamily ***families,
                                       int *n_families)

     PangoFontMetrics *pango_context_get_metrics(PangoContext *context,
                                                 PangoFontDescription *desc,
                                                 PangoLanguage *language)

     PangoLanguage *pango_context_get_language(PangoContext *c)

     void pango_context_set_language(PangoContext               *context,
                                     PangoLanguage              *language)

     PangoFontset *pango_context_load_fontset(PangoContext *c,
                                              PangoFontDescription *d,
                                              PangoLanguage *l)

     void pango_context_set_font_description(PangoContext *c,
                                             PangoFontDescription *d)

     void pango_context_set_base_dir(PangoContext *c, PangoDirection dir)

     #
     # Layout
     #
     ctypedef enum PangoAlignment:
          PANGO_ALIGN_LEFT,
          PANGO_ALIGN_CENTER,
          PANGO_ALIGN_RIGHT

     ctypedef enum PangoWrapMode:
          PANGO_WRAP_WORD,
          PANGO_WRAP_CHAR,
          PANGO_WRAP_WORD_CHAR


     ctypedef enum PangoEllipsizeMode:
          PANGO_ELLIPSIZE_NONE,
          PANGO_ELLIPSIZE_START,
          PANGO_ELLIPSIZE_MIDDLE,
          PANGO_ELLIPSIZE_END

     ctypedef struct PangoLayout
     ctypedef struct PangoLayoutLine

     PangoLayout *pango_layout_new(PangoContext *context)
     PangoContext *pango_layout_get_context(PangoLayout *layout)

     void pango_layout_set_text(PangoLayout *layout,
                                char *text,
                                int  length)
     char *pango_layout_get_text(PangoLayout *layout)
     void pango_layout_set_markup(PangoLayout *layout,
                                  char *markup,
                                  int length)
     void pango_layout_set_font_description (PangoLayout *layout,
                                             PangoFontDescription *desc)

     void pango_layout_set_width(PangoLayout                *layout,
                                 int                         width)
     int pango_layout_get_width(PangoLayout                *layout)
     void pango_layout_set_wrap(PangoLayout                *layout,
                                PangoWrapMode               wrap)
     void pango_layout_set_indent(PangoLayout *layout,
                                  int                         indent)
     void pango_layout_set_spacing(PangoLayout                *layout,
                                   int                         spacing)
     void pango_layout_set_justify(PangoLayout *layout,
                                   int justify)
     void pango_layout_set_auto_dir(PangoLayout *layout,
                                    int auto_dir)
     void pango_layout_set_alignment(PangoLayout                *layout,
                                     PangoAlignment              alignment)
     void pango_layout_set_single_paragraph_mode (PangoLayout *layout,
                                                  int setting)
     void pango_layout_set_ellipsize (PangoLayout *layout,
                                      PangoEllipsizeMode  ellipsize)

     void pango_layout_get_size (PangoLayout    *layout,
                                 int            *width,
                                 int            *height)
     void pango_layout_get_pixel_size (PangoLayout    *layout,
                                       int            *width,
                                       int            *height)

     void pango_layout_get_extents (PangoLayout    *layout,
                                    PangoRectangle *ink_rect,
                                    PangoRectangle *logical_rect)
     void pango_layout_get_pixel_extents (PangoLayout    *layout,
                                          PangoRectangle *ink_rect,
                                          PangoRectangle *logical_rect)



cdef extern from "pango/pangoft2.h":
     #
     # FontMap
     #
     PangoContext *pango_ft2_font_map_create_context(PangoFontMap *map)
     PangoFontMap *pango_ft2_font_map_new()
     void pango_ft2_font_map_set_resolution(PangoFontMap *map,
                                            double dpi_x,
                                            double dpi_y)

     void pango_ft2_render_layout(FT_Bitmap        *bitmap,
                                  PangoLayout      *layout,
                                  int               x,
                                  int               y)

     void pango_ft2_render_layout_subpixel(FT_Bitmap        *bitmap,
                                           PangoLayout      *layout,
                                           int               x,
                                           int               y)

     void pango_ft2_render_layout_line(FT_Bitmap        *bitmap,
                                       PangoLayoutLine      *layout,
                                       int               x,
                                       int               y)

     void pango_ft2_render_layout_line_subpixel(FT_Bitmap        *bitmap,
                                                PangoLayoutLine  *layout,
                                                int               x,
                                                int               y)

from cStringIO import StringIO

cdef class ChimeraBitmap:
     # A wrapper around the FT_Bitmap combined with the needs of
     # Pango and Chimera
     cdef FT_Bitmap *_bitmap
     def __new__(self, width, height):
          self._bitmap = <FT_Bitmap *>g_malloc0(sizeof(FT_Bitmap))
          self._bitmap.buffer = <char *>g_malloc0(width * height * sizeof(char*))

          self._bitmap.rows = height
          self._bitmap.width = width
          self._bitmap.pitch = width
          self._bitmap.num_grays = 256
          self._bitmap.pixel_mode = FT_PIXEL_MODE_GRAY

     def __dealloc__(self):
          g_free(self._bitmap.buffer)
          g_free(self._bitmap)


     cdef FT_Bitmap *getBitmap(self):
          return self._bitmap

     property size:
          def __get__(self):
               return (self._bitmap.width,
                       self._bitmap.rows
                       )
     def __repr__(self):
          return  "<ChimeraBitmap (%s, %s)>" % (self._bitmap.width,
                                                self._bitmap.rows
                                                )

     def toPngFilename(self, filename):
          file = open(filename, 'w')
          file.write(self.toPngFile().read())
          file.close()

     def toPngFile(self):
          cdef PngFile png
          png = PngFile(<object>self.getBitmap())
          buffer = StringIO()
          png.writeFile(buffer)
          buffer.seek(0)
          return buffer

     def toPgmFilename(self, filename):
          cdef int i, j, length
          file = open(filename, 'w')

          data = PyString_FromStringAndSize(self._bitmap.buffer,
                                     (self._bitmap.rows *
                                      self._bitmap.width))
          file.write("P5\n")
          file.write("%d %d\n" % (self._bitmap.width,
                                  self._bitmap.rows))
          file.write("254\n")
          file.write(data)
          file.close()

     def toAsciiFilename(self, filename):
          cdef png_byte **rows
          cdef FT_Bitmap *bitmap
          cdef int i, j
          fp = open(filename, 'w')
          bitmap = self._bitmap

          rows = <png_byte **>g_malloc(bitmap.rows * sizeof(png_byte*))
          for i from 0 <= i < bitmap.rows:
               rows[i] = bitmap.buffer + (i * bitmap.width)

          fp.write("w %s h%s\n" %(bitmap.width, bitmap.rows))
          for i from 0 <= i < bitmap.rows:
               for j from 0 <= j < bitmap.width:
                    x = rows[i][j]
                    fp.write("%04x" % x)
               fp.write('\n')
          fp.close()
          g_free(rows)

cdef class FontConfig:
    """Using a FontConfig Instance you can (before making pango
    objects) add applcation specific fonts and font directories
    that can then be resovled as normal.

    >>> FontConfig().addFontDir("/fonts")

    """

    cdef FcConfig *_fc

    def __new__(self):
        self._fc = FcConfigGetCurrent()

    def addFontFile(self, filename):
        FcConfigAppFontAddFile(self._fc, filename)

    def addFontDir(self, dirname):
        FcConfigAppFontAddDir(self._fc, dirname)


cdef class Pango:
     cdef PangoContext *_context
     cdef PangoFontMap *_fm
     cdef PangoFontDescription *_fd

     def __new__(self, font=None, lang="en_US", dpi=96):
          # Here we have hardcoded typical screen resolution
          # this may have to be exposed so we can do higher DPI
          # renderings
          self._fm = pango_ft2_font_map_new()
          pango_ft2_font_map_set_resolution(self._fm, dpi, dpi)
          self._context = pango_ft2_font_map_create_context(self._fm)
          # This would have to be exposed along with alignment
          pango_context_set_base_dir(self._context, PANGO_DIRECTION_LTR)
          self.set_language(lang)
          if font: self.set_font(font)

     cdef __dealloc__(self):
          pango_font_description_free (self._fd)
          g_object_unref(self._fm)
          g_object_unref(self._context)

     def set_language(self, langstr):
          cdef PangoLanguage *lang
          lang = pango_language_from_string(langstr)
          pango_context_set_language(self._context, lang)

     def set_font(self, fontstr):
          cdef PangoFontDescription *fd

          fd = pango_font_description_from_string(fontstr)
          if not fd: raise ValueError("invalid font desc '%s'" %fontstr)
          self._fd = fd
          pango_context_load_fontset(self._context,
                                     fd,
                                     pango_context_get_language(self._context))

     def set_font_description(self, family, size):
          cdef PangoFontDescription *font_description
          font_description = pango_font_description_new();
          pango_font_description_set_family (font_description, family);
          pango_font_description_set_style (font_description, PANGO_STYLE_NORMAL);
          pango_font_description_set_variant (font_description, PANGO_VARIANT_NORMAL);
          pango_font_description_set_weight (font_description, PANGO_WEIGHT_NORMAL);
          pango_font_description_set_stretch (font_description, PANGO_STRETCH_NORMAL);
          pango_font_description_set_size (font_description, size * PANGO_SCALE);

          pango_context_set_font_description (self._context, font_description);
          self._fd = font_description

     def render_text(self, text, maxwidth=None, markup=None):
          cdef PangoLayout *layout
          cdef FT_Bitmap *bitmap
          cdef char *buf
          cdef int width, height
          cdef ChimeraBitmap cbit
          cdef PangoRectangle logical_rect

          if type(text) == unicode:
               text = text.encode('utf8')

          layout = pango_layout_new(self._context)
          pango_layout_set_font_description(layout, self._fd)
          pango_layout_set_alignment(layout,
                                     PANGO_ALIGN_LEFT)
          pango_layout_set_single_paragraph_mode(layout, 1)
          if maxwidth != None:
               pango_layout_set_width(layout, maxwidth * PANGO_SCALE)

          if markup:
               pango_layout_set_markup(layout, text, len(text))
          else:
               pango_layout_set_text(layout, text, len(text))
          pango_layout_get_pixel_size(layout, &width, &height)

          cbit = ChimeraBitmap(width, height)
          bitmap = (<FT_Bitmap*>cbit.getBitmap())
          pango_ft2_render_layout_subpixel(bitmap,
                                  layout,
                                  0, 0);
          g_object_unref(layout)
          return cbit


     def list_families(self):
          cdef PangoFontFamily **fams
          cdef int ct, i

          pango_context_list_families(self._context,
                                      &fams,
                                      &ct)
          results = []
          for i from 0 <= i < ct:
               results.append(pango_font_family_get_name(fams[i]))

          g_free(fams)
          return results



cdef class PangoCairo:
     # Using the cairo renderer with Pango
     # highest quality, most features
     # I intentionally only expose a subset of the full functionality
     # until I understand the set of use cases worth supporting
     cdef cairo_t *context
     cdef cairo_image_surface_t
     cdef PangoLayout *layout
     cdef PangoFontDescription *desc

     def __new__(self, font=None, lang="en_US", dpi=96):
          self.context = cairo_create()
          PangoLayout *layout
          PangoFontDescription *desc
