# Author:    Lisandro Dalcin
# Contact:   dalcinl@gmail.com
# Copyright: This module has been placed in the public domain.
# Id:        $Id: _rtld.py 160 2007-12-13 18:51:48Z dalcinl $

import sys as _sys

getdlopenflags = getattr(_sys, 'getdlopenflags', lambda  : 0)
setdlopenflags = getattr(_sys, 'setdlopenflags', lambda n: None)

try:
    from DLFCN import RTLD_GLOBAL
except ImportError:
    try:
        from dl import RTLD_GLOBAL
    except ImportError:
        try:
            from _ctypes import RTLD_GLOBAL
        except ImportError:
            try:
                from ctypes import RTLD_GLOBAL
            except ImportError:
                RTLD_GLOBAL = 0

RTLD_PYFLAG = getdlopenflags()
setdlopenflags(RTLD_PYFLAG | RTLD_GLOBAL)
try:
    from mpi4py import libmpi
finally:
    setdlopenflags(RTLD_PYFLAG)
