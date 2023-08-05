cdef extern from "fontconfig/fontconfig.h":
     cdef struct FcConfig
     FcConfig * FcConfigGetCurrent()

     void FcConfigAppFontClear  (FcConfig            *config)
     int FcConfigAppFontAddFile (FcConfig *config, char *file)
     int FcConfigAppFontAddDir  (FcConfig *config, char *dir)

