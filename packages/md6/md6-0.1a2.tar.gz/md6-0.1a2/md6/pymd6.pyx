# MD6 Python wrapper
# Copyright (c) 2009 Christian Heimes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

cdef extern from "md6.h" nogil:
    ctypedef unsigned long uint64_t
     
    ctypedef struct md6_state:
        char *hashval
        char *hexhashval

    int md6_init(md6_state *st, 
                 int d)
    int md6_full_init(md6_state *st,
			          int d,
			          unsigned char *key,
			          int keylen,
			          int L,
			          int r)

    int md6_update(md6_state *st,
                   unsigned char *data,
                   uint64_t databitlen)

    int md6_final(md6_state *st,
                  char *hashval)

    int md6_default_r(int d, 
			          int keylen)

    int md6_default_L

    int MD6_SUCCESS
    int MD6_FAIL
    int MD6_BADHASHLEN
    int MD6_NULLSTATE
    int MD6_BADKEYLEN
    int MD6_STATENOTINIT
    int MD6_STACKUNDERFLOW
    int MD6_STACKOVERFLOW
    int MD6_NULLDATA
    int MD6_NULL_N
    int MD6_NULL_B
    int MD6_BAD_ELL
    int MD6_BAD_p
    int MD6_NULL_K
    int MD6_NULL_Q
    int MD6_NULL_C
    int MD6_BAD_L 
    int MD6_BAD_r
    int MD6_OUT_OF_MEMORY


cdef extern from "stdlib.h" nogil:
    cdef int memcpy(void *dest, void *src, unsigned n)
    cdef void* malloc(unsigned int)
    cdef void free(void*)


_errcode_map = {
    MD6_FAIL: "some other problem",
    MD6_BADHASHLEN: "hashbitlen<1 or >512 bits",
    MD6_NULLSTATE: "null state passed to MD6",
    MD6_BADKEYLEN: "key length is <0 or >512 bits",
    MD6_STATENOTINIT: "state was never initialized",
    MD6_STACKUNDERFLOW: "MD6 stack underflows (shouldn't happen)",
    MD6_STACKOVERFLOW: "MD6 stack overflow (message too long)",
    MD6_NULLDATA: "null data pointer",
    MD6_NULL_N: "compress: N is null",
    MD6_NULL_B: "standard compress: null B pointer",
    MD6_BAD_ELL: "standard compress: ell not in {0,255}",
    MD6_BAD_p: "standard compress: p<0 or p>b*w",
    MD6_NULL_K: "standard compress: K is null",
    MD6_NULL_Q: "standard compress: Q is null",
    MD6_NULL_C: "standard compress: C is null",
    MD6_BAD_L: "standard compress: L <0 or > 255, md6_init: L<0 or L>255",
    MD6_BAD_r: "compress: r<0 or r>255, md6_init: r<0 or r>255",
    MD6_OUT_OF_MEMORY: "compress: storage allocation failed",
    }


class MD6Exception(Exception):
    def __init__(self, errorcode):
        msg = _errcode_map.get(errorcode, "Unknown error")
        Exception.__init__(self, msg)
        self.errorcode = errorcode


cdef class MD6(object):
    cdef readonly name
    cdef readonly int digest_size
    cdef md6_state *st
    
    def __cinit__(self, int digest_size):
        cdef int result

        self.st = <md6_state*>malloc(sizeof(md6_state))

        with nogil:
            result = md6_init(self.st, digest_size)
        if result != 0:
            raise MD6Exception(result)

        self.digest_size = digest_size
        self.name = "md6_%s" % digest_size
        
    def __dealloc__(self):
        if self.st is not NULL:
            free(self.st)

    def update(self, char *data):
        cdef unsigned char* udata
        cdef uint64_t datalen
        cdef int result
        
        udata = <unsigned char*>data 
        datalen = <uint64_t>len(data)
        with nogil:
            # oh yeah, the third argument is the data BIT lenght
            result = md6_update(self.st, udata, datalen*8)
        if result != 0:
            raise MD6Exception(result)

    def digest(self):
        cdef md6_state localst
        cdef int result
        
        # md6_final() finalizes the state. Updates are no longer possible.
        # Workaround: copy the state first, then finalize the copy in order
        # to access the hash.
        memcpy(&localst, self.st, sizeof(md6_state))
        with nogil:
            result = md6_final(&localst, NULL)
        if result != 0:
            raise MD6Exception(result)
           
        return <char*>localst.hashval
        
    def hexdigest(self):
        cdef md6_state localst
        cdef int result
        
        memcpy(&localst, self.st, sizeof(md6_state))
        with nogil:
            result = md6_final(&localst, NULL)
        if result != 0:
            raise MD6Exception(result)

        return <char*>localst.hexhashval
        
    def copy(self):
        cdef MD6 clone
        clone = self.__class__(self.digest_size)
        memcpy(clone.st, self.st, sizeof(md6_state))
        return clone

    def __repr__(self):
        return "<%s at %i" % (self.name, id(self))
