cdef extern from "Python.h":
     object PyString_FromStringAndSize(char *s, int len)
     char * PyString_AsString(object str)
