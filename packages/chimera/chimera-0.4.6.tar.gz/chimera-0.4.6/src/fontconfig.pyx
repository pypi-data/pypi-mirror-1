
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

