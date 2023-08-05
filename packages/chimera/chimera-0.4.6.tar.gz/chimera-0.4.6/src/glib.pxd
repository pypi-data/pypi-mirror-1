cdef extern from "glib.h":
     ctypedef struct GError:
          int code
          char *message

     void g_error_free(GError *error)

     ctypedef struct GList
     int g_list_length(GList *list)
     void * g_list_nth_data(GList *list, int offset)

     ctypedef struct GSList:
         void *data
         GSList *next

     void g_slist_free(GSList *l)

     void *g_malloc(long n_bytes)
     void *g_malloc0(long n_bytes)
     void g_free(void *ptr)
     void g_object_unref(void *instance)

     ctypedef int guint16
     ctypedef int gboolean

