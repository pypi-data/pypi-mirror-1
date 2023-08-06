"""
General PyAFS utilities, such as error handling
"""

import sys

# otherwise certain headers are unhappy
cdef extern from "netinet/in.h": pass
cdef extern from "afs/vice.h": pass

cdef int _init = 0

# pioctl convenience wrappers

cdef extern int pioctl_read(char *dir, afs_int32 op, void *buffer, unsigned short size, afs_int32 follow) except -1:
    cdef ViceIoctl blob
    cdef afs_int32 code
    blob.in_size  = 0
    blob.out_size = size
    blob.out = buffer
    code = pioctl(dir, op, &blob, follow)
    # This might work with the rest of OpenAFS, but I'm not convinced
    # the rest of it is consistent
    if code == -1:
        raise OSError(errno, strerror(errno))
    pyafs_error(code)
    return code

cdef extern int pioctl_write(char *dir, afs_int32 op, char *buffer, afs_int32 follow) except -1:
    cdef ViceIoctl blob
    cdef afs_int32 code
    blob.cin = buffer
    blob.in_size = 1 + strlen(buffer)
    blob.out_size = 0
    code = pioctl(dir, op, &blob, follow)
    # This might work with the rest of OpenAFS, but I'm not convinced
    # the rest of it is consistent
    if code == -1:
        raise OSError(errno, strerror(errno))
    pyafs_error(code)
    return code

# Error handling

class AFSException(Exception):
    def __init__(self, errno):
        self.errno = errno
        self.strerror = afs_error_message(errno)

    def __repr__(self):
        return "AFSException(%s)" % (self.errno)

    def __str__(self):
        return "[%s] %s" % (self.errno, self.strerror)

def pyafs_error(code):
    if not _init:
        initialize_ACFG_error_table()
        initialize_KTC_error_table()
        initialize_PT_error_table()
        initialize_RXK_error_table()
        initialize_U_error_table()

        _init = 1

    if code != 0:
        raise AFSException(code)
