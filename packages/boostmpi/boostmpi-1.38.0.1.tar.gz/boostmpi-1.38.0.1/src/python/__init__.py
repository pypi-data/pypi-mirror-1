import sys

if sys.platform == 'linux2':
    import DLFCN as dl
    flags = sys.getdlopenflags()
    sys.setdlopenflags(dl.RTLD_NOW|dl.RTLD_GLOBAL)
    from boostmpi._internal import *
    sys.setdlopenflags(flags)
else:
    from boostmpi._internal import *
 
import boostmpi._internal

from boostmpi._internal import __doc__, __author__, __copyright__, __license__

__all__ = [n for n in dir(boostmpi._internal) if not n.startswith("_")]
