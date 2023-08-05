cdef extern from "stddef.h":
     ctypedef int size_t

cdef extern from "stdio.h":
     ctypedef struct FILE
     void printf(char *fmt, ...)

cdef extern from "glib.h":
     ctypedef struct GError:
          int code
          char *message

     void g_error_free(GError *error)

     ctypedef struct GList
     int g_list_length(GList *list)
     void * g_list_nth_data(GList *list, int offset)

     void *g_malloc(long n_bytes)
     void *g_malloc0(long n_bytes)
     void g_free(void *ptr)
     void g_object_unref(void *instance)

cdef extern from "Python.h":
     object PyString_FromStringAndSize(char *s, int len)
     FILE *PyFile_AsFile(object)

cdef extern from "ft2build.h":
     pass

cdef extern from "freetype/freetype.h":
     ctypedef struct FT_Bitmap:
          int rows
          int width
          int pitch
          char *buffer
          int num_grays
          char pixel_mode
          char palette_mode
          void *palette

     ctypedef enum FT_Pixel_Mode:
          FT_PIXEL_MODE_NONE = 0,
          FT_PIXEL_MODE_MONO,
          FT_PIXEL_MODE_GRAY,
          FT_PIXEL_MODE_GRAY2,
          FT_PIXEL_MODE_GRAY4,
          FT_PIXEL_MODE_LCD,
          FT_PIXEL_MODE_LCD_V,
          FT_PIXEL_MODE_MAX

cdef extern from "fontconfig/fontconfig.h":
     cdef struct FcConfig
     FcConfig * FcConfigGetCurrent()

     int FcConfigAppFontAddFile (FcConfig *config, char *file)
     int FcConfigAppFontAddDir (FcConfig *config, char *dir)

