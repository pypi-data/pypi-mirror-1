"""
chimera_png
~~~~~~~~~~~~~~~~~~~~
A library for PNG manipulation for ChimeraBuffers

"""

__author__ = 'Benjamin Saller <bcsaller@objectrealms.net>'
__docformat__ = 'restructuredtext'
__copyright__ = 'Copyright ObjectRealms, LLC. 2005.'
__license__  = 'The GNU Public License V2+'

include "common.pyi"

PNG_LIBPNG_VER_STRING="1.2.8"

PNG_COLOR_MASK_ALPHA=4
PNG_COLOR_MASK_COLOR=2
PNG_COLOR_MASK_PALETTE=1
PNG_COLOR_TYPE_GRAY_ALPHA=( PNG_COLOR_MASK_ALPHA )
PNG_COLOR_TYPE_GA=PNG_COLOR_TYPE_GRAY_ALPHA
PNG_COLOR_TYPE_GRAY=0
PNG_COLOR_TYPE_PALETTE=( PNG_COLOR_MASK_COLOR |
                         PNG_COLOR_MASK_PALETTE )
PNG_COLOR_TYPE_RGB=( PNG_COLOR_MASK_COLOR )
PNG_COLOR_TYPE_RGB_ALPHA=( PNG_COLOR_MASK_COLOR |
                           PNG_COLOR_MASK_ALPHA )
PNG_COLOR_TYPE_RGBA=PNG_COLOR_TYPE_RGB_ALPHA

PNG_COMPRESSION_TYPE_BASE=0
PNG_COMPRESSION_TYPE_DEFAULT=PNG_COMPRESSION_TYPE_BASE

PNG_TEXT_COMPRESSION_NONE=-1

PNG_INTERLACE_ADAM7=1
PNG_INTERLACE_LAST=2
PNG_INTERLACE_NONE=0

PNG_FILTER_TYPE_BASE=0
PNG_FILTER_TYPE_DEFAULT=PNG_FILTER_TYPE_BASE
PNG_FILTER_VALUE_AVG=3
PNG_FILTER_VALUE_LAST=5
PNG_FILTER_VALUE_NONE=0
PNG_FILTER_VALUE_PAETH=4
PNG_FILTER_VALUE_SUB=1
PNG_FILTER_VALUE_UP=2

cdef extern from "png.h":

    ctypedef struct png_struct
    ctypedef struct png_info
    ctypedef char png_byte
    ctypedef void (*png_rw_ptr) (png_struct *p, png_byte *b,
                                 int s)
    ctypedef void (*png_flush_ptr) (png_struct *p)
    ctypedef void (*png_error_ptr) (png_struct *p, char *s)

    ctypedef struct png_text:
        char *key
        char *text
        int compression

    ctypedef struct png_color_8:
        png_byte red
        png_byte green
        png_byte blue
        png_byte gray
        png_byte alpha



    png_struct *png_create_write_struct(char *version,
                                        void *error_ptr,
                                        png_error_ptr error_fn,
                                        png_error_ptr warn_fn)

    png_info *png_create_info_struct(png_struct *p)
    void png_init_io(png_struct *png, void *file_pointer)

    void png_set_write_fn(png_struct *png,
                     void *file_pointer,
                     png_rw_ptr write_fn,
                     png_flush_ptr flush_fn)

    void png_set_IHDR(png_struct *s, png_info *i,
                 int width,
                 int height,
                 int bit_depth,
                 int color_type,
                 int interlace_method,
                 int compression_method,
                 int filter_method)

    void png_set_text(png_struct *p, png_info *i, png_text *t, int ct)
    void png_write_tEXt (png_struct *p, char *key, char *text, int
                         size)

    void png_set_sBIT(png_struct *p, png_info *i, png_color_8
                      *sig_bit)

    void png_set_packing(png_struct *png)
    void png_set_gray_1_2_4_to_8(png_struct *png)

    void png_set_invert_mono(png_struct *png)
    void png_write_info(png_struct *png, png_info *info)
    void png_write_image(png_struct *png, char **rows)
    void png_write_row(png_struct *png, png_byte *r)
    void png_write_end(png_struct *png, png_info *info)

    void png_destroy_write_struct(png_struct **png, png_info **info)

    void *png_get_io_ptr(png_struct *s)



cdef writeFile(png_struct *png, png_byte *data, int length):
    fp = <object> png_get_io_ptr(png)
    string = PyString_FromStringAndSize(data, length)
    fp.write(string)

cdef flushFile(png_struct *png):
    fp = <object> png_get_io_ptr(png)
    fp.flush()

cdef class PngFile:
    cdef png_byte **rows
    cdef png_struct *png
    cdef png_info *info

    def __new__(self, bitmapObj):
        cdef FT_Bitmap *bitmap
        cdef int i

        bitmap = <FT_Bitmap*>bitmapObj
        self.rows = <png_byte **>g_malloc0(bitmap.rows * sizeof(png_byte*))

        # set up a virtual grid of pointers
        for i from 0 <= i < bitmap.rows:
            self.rows[i] = bitmap.buffer + i * bitmap.pitch

        self.png = png_create_write_struct(PNG_LIBPNG_VER_STRING,
                                           NULL, NULL, NULL)
        self.info = png_create_info_struct(self.png)

        png_set_IHDR(self.png, self.info,
                     bitmap.width, bitmap.rows, 8,
                     PNG_COLOR_TYPE_GRAY,
                     PNG_INTERLACE_NONE,
                     PNG_COMPRESSION_TYPE_DEFAULT,
                     PNG_FILTER_TYPE_BASE)
        png_set_invert_mono(self.png)


    def __dealloc__(self):
        g_free(self.rows)
        png_destroy_write_struct(&self.png, &self.info)

    def writeFile(self, file, title=''):
        cdef int i
        text = ( ('Title',    title),
                 ('Software', 'Chimera'),
                 ('Producer', 'ObjectRealms')
                 )

        png_init_io(self.png, <void *>file)
        png_set_write_fn(self.png, <void *>file, <png_rw_ptr>writeFile, <png_flush_ptr>flushFile)

        png_write_info (self.png, self.info)
        for key, value in text:
            png_write_tEXt(self.png, key, value, len(value))

        png_write_image (self.png, self.rows)
        png_write_end (self.png, self.info)

        return


