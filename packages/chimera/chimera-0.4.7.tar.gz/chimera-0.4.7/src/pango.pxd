cimport cairo
from glib cimport guint16, gboolean, GSList

cdef extern from "pango/pango.h":
     #
     # Extents
     #
     ctypedef struct PangoRectangle:
          int x
          int y
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



     ctypedef struct PangoFont
     ctypedef struct PangoFontDescription
     ctypedef struct PangoFontMetrics
     ctypedef struct PangoFontset
     ctypedef struct PangoFontFamily
     ctypedef struct PangoAttrList
     ctypedef struct PangoFontFace
     ctypedef struct PangoAttribute:
         int start_index
         int end_index

     ctypedef struct PangoAttrIterator


     #
     # Font Desc
     #
     char * pango_font_family_get_name(PangoFontFamily *family)

     PangoFontDescription *pango_font_description_new()
     PangoFontDescription *pango_font_description_from_string (char
                                                               *str)
     char *pango_font_description_to_string (PangoFontDescription *fd)
     char *pango_font_description_to_filename (PangoFontDescription *fd)

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

     void pango_font_family_list_faces(PangoFontFamily *family,
                                       PangoFontFace ***faces,
                                       int *n_faces)
     char *pango_font_face_get_face_name(PangoFontFace *face)

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


     ctypedef enum PangoUnderline:
         PANGO_UNDERLINE_NONE,
         PANGO_UNDERLINE_SINGLE,
         PANGO_UNDERLINE_DOUBLE,
         PANGO_UNDERLINE_LOW,
         PANGO_UNDERLINE_ERROR

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

     void pango_layout_set_attributes (PangoLayout    *layout,
                                       PangoAttrList  *attrs)
     PangoAttrList *pango_layout_get_attributes (PangoLayout *layout)


     void pango_layout_set_text(PangoLayout *layout,
                                char *text,
                                int  length)
     char *pango_layout_get_text(PangoLayout *layout)

     void pango_layout_set_markup(PangoLayout *layout,
                                  char *markup,
                                  int length)

     PangoFontDescription *pango_layout_get_font_description(PangoLayout *layout)
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

     int pango_layout_get_line_count(PangoLayout *layout)

     void pango_layout_context_changed(PangoLayout *layout)


     #
     # Attributes
     #
     PangoAttrList *    pango_attr_list_new           ()
     PangoAttrList *    pango_attr_list_ref           (PangoAttrList  *list)
     void               pango_attr_list_unref         (PangoAttrList  *list)
     PangoAttrList *    pango_attr_list_copy          (PangoAttrList  *list)
     void               pango_attr_list_insert        (PangoAttrList  *list,
                                                       PangoAttribute *attr)
     void               pango_attr_list_change        (PangoAttrList *list,
                                                       PangoAttribute *attr)

     PangoAttribute *pango_attr_language_new      (PangoLanguage              *language)
     PangoAttribute *pango_attr_family_new        (char  *family)
     PangoAttribute *pango_attr_foreground_new    (guint16                     red,
                                                   guint16                     green,
                                                   guint16                     blue)
     PangoAttribute *pango_attr_background_new    (guint16                     red,
                                                   guint16                     green,
                                                   guint16                     blue)
     PangoAttribute *pango_attr_size_new          (int                         size)
     PangoAttribute *pango_attr_size_new_absolute (int                         size)
     PangoAttribute *pango_attr_style_new         (PangoStyle                  style)
     PangoAttribute *pango_attr_weight_new        (PangoWeight                 weight)
     PangoAttribute *pango_attr_variant_new       (PangoVariant                variant)
     PangoAttribute *pango_attr_stretch_new       (PangoStretch                stretch)
     PangoAttribute *pango_attr_font_desc_new     (PangoFontDescription *desc)

     PangoAttribute *pango_attr_underline_new           (PangoUnderline underline)
     PangoAttribute *pango_attr_underline_color_new     (guint16        red,
                                                         guint16        green,
                                                         guint16        blue)
     PangoAttribute *pango_attr_strikethrough_new       (gboolean       strikethrough)
     PangoAttribute *pango_attr_strikethrough_color_new (guint16        red,
                                                         guint16        green,
                                                         guint16        blue)

     PangoAttribute *pango_attr_rise_new          (int        rise)
     PangoAttribute *pango_attr_scale_new         (double     scale_factor)
     PangoAttribute *pango_attr_fallback_new      (gboolean   enable_fallback)
     PangoAttribute *pango_attr_letter_spacing_new (int       letter_spacing)

     PangoAttrIterator *pango_attr_list_get_iterator  (PangoAttrList  *list)
     GSList *pango_attr_iterator_get_attrs(PangoAttrIterator *i)
     void pango_attr_iterator_destroy(PangoAttrIterator *i)

     #
     # Pango Cairo (where rubber meets road)
     #
cdef extern from "pango/pangocairo.h":
     ctypedef struct PangoCairoFontMap

     PangoFontMap *pango_cairo_font_map_new         ()
     PangoFontMap *pango_cairo_font_map_get_default ()
     void          pango_cairo_font_map_set_resolution (PangoCairoFontMap *fontmap,
                                                        double             dpi)
     double        pango_cairo_font_map_get_resolution (PangoCairoFontMap *fontmap)
     PangoContext *pango_cairo_font_map_create_context (PangoCairoFontMap *fontmap)


     void         pango_cairo_update_context (cairo.cairo_t      *cr,
                                              PangoContext *context)

     void         pango_cairo_context_set_font_options (PangoContext               *context,
                                                        cairo.cairo_font_options_t *options)
     cairo.cairo_font_options_t *pango_cairo_context_get_font_options (PangoContext     *context)
     void  pango_cairo_context_set_resolution     (PangoContext       *context,
                                                   double              dpi)
     double       pango_cairo_context_get_resolution     (PangoContext       *context)

     PangoLayout *pango_cairo_create_layout (cairo.cairo_t     *cr)
     void         pango_cairo_update_layout (cairo.cairo_t     *cr,
                                             PangoLayout *layout)

     #
     # Rendering
     #
     void pango_cairo_show_layout       (cairo.cairo_t          *cr,
                                         PangoLayout      *layout)

     #
     # to a Path
     #
     void pango_cairo_layout_path       (cairo.cairo_t          *cr,
                                         PangoLayout      *layout)

