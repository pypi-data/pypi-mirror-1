# $Header: /home/cvs2/mysql/mysql/libc.pxi,v 1.3 2006/08/26 20:19:51 ehuss Exp $

# XXX: BUG
#      This must be imported after python.pxi because of size_t.
#      UGH!
cdef extern from "string.h":

    void * memset (void *b, int c, size_t len)
    void * memcpy (void *dst, void *src, size_t len)

cdef extern from "stdlib.h":

    void abort ()
