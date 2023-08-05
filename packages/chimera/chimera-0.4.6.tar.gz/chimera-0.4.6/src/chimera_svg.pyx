"""
chimera_svg
~~~~~~~~~~~~~~~~~~~~
A library for SVG loading

"""

__author__ = 'Benjamin Saller <bcsaller@objectrealms.net>'
__docformat__ = 'restructuredtext'
__copyright__ = 'Copyright ObjectRealms, LLC. 2005.'
__license__  = 'The GNU Public License V2+'

include "glib.pxd"
include "python.pxd"
import StringIO

cdef extern from "gdk-pixbuf/gdk-pixbuf.h":
    ctypedef struct GdkPixbuf

    ctypedef enum GdkColorspace:
        GDK_COLORSPACE_RGB

    GdkPixbuf *gdk_pixbuf_new (GdkColorspace colorspace,
                               int has_alpha,
                               int bits_per_sample,
                               int width,
                               int height)

    int gdk_pixbuf_save_to_bufferv(GdkPixbuf *pixbuf,
                                   int      **buffer,
                                   int       *buffer_size,
                                   char      *type,
                                   char     **option_keys,
                                   char     **option_values,
                                   GError   **error)


cdef extern from "librsvg/rsvg.h":
    void rsvg_init()

    GdkPixbuf  *rsvg_pixbuf_from_file                  (char  *file_name,
                                                        GError      **error)
    GdkPixbuf  *rsvg_pixbuf_from_file_at_zoom          (char  *file_name,
                                                        double        x_zoom,
                                                        double        y_zoom,
                                                        GError      **error)
    GdkPixbuf  *rsvg_pixbuf_from_file_at_size          (char  *file_name,
                                                        int          width,
                                                        int          height,
                                                        GError      **error)
    GdkPixbuf  *rsvg_pixbuf_from_file_at_max_size      (char  *file_name,
                                                        int          max_width,
                                                        int          max_height,
                                                        GError      **error)
    GdkPixbuf  *rsvg_pixbuf_from_file_at_zoom_with_max (char  *file_name,
                                                        double        x_zoom,
                                                        double        y_zoom,
                                                        int          max_width,
                                                        int          max_height,
                                                        GError      **error)


def chimera_svg_init():
    rsvg_init()

cdef class ChimeraSvg:
    cdef GdkPixbuf *pixbuf

    def load(self, filename):
        cdef GError *error
        error = NULL

        self.pixbuf = rsvg_pixbuf_from_file(filename, NULL)

        if error != NULL:
            msg = error[0].message
            g_error_free(error)
            raise ValueError(msg)

        result = self._toImage(self.pixbuf)
        return result

    def load_at_size(self, char *filename, int width, int height):
        cdef GError *error
        error = NULL
        self.pixbuf = rsvg_pixbuf_from_file_at_size(filename,
                                                    width,
                                                    height,
                                                    &error)

        if error != NULL:
            msg = error[0].message
            g_error_free(error)
            raise ValueError(msg)

        result = self._toImage(self.pixbuf)
        return result

    def load_at_maxsize(self, char *filename, int width, int height):
        cdef GError *error
        error = NULL
        self.pixbuf = rsvg_pixbuf_from_file_at_max_size(filename,
                                                        width,
                                                        height,
                                                        &error)

        if error != NULL:
            msg = error[0].message
            g_error_free(error)
            raise ValueError(msg)

        return self.image

    def load_at_zoom_with_max(self, char *filename,
                              double xzoom, double yzoom,
                              int xmax, int ymax):
        cdef GError *error
        error = NULL
        self.pixbuf = rsvg_pixbuf_from_file_at_zoom_with_max(filename,
                                                             xzoom, yzoom,
                                                             xmax, ymax,
                                                             &error)

        if error != NULL:
            msg = error[0].message
            g_error_free(error)
            raise ValueError(msg)

        return self.image

    property image:
        def __get__(self):
            cdef GdkPixbuf *p
            p = self.pixbuf
            return self._toImage(p)
        
    cdef _toImage(self, GdkPixbuf *pixbuf):
        # XXX: I do some crazy buffering here, fix it later
        # using a save callback that write to a StringIO/File
        cdef int *buffer, size

        gdk_pixbuf_save_to_bufferv(pixbuf, &buffer, &size,
                                   "png", NULL, NULL, NULL)
        # we should now have a png in a buffer of size
        # lets return a StringIO object
        string = PyString_FromStringAndSize(<char *>buffer, size)

        output = StringIO.StringIO(string)
        output.seek(0)
        g_free(buffer)
        return output
