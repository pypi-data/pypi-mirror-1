cdef extern from "stddef.h":
     ctypedef int size_t

cdef extern from "stdio.h":
     ctypedef struct FILE
     void printf(char *fmt, ...)

     void memset(void *p, char c, int len)

cdef extern from "string.h":
     void *memcpy(void *dest, void *src, size_t n)
