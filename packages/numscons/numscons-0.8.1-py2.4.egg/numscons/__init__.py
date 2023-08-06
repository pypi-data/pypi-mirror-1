#! /usr/bin/env python
# Last Change: Fri Mar 07 02:00 PM 2008 J

"""numscons is a package which enable building python extensions within
distutils. It is intented as a replacement of numpy.distutils to build numpy
with more flexibility, and in a more robust mannter."""

import core
from core import *
__all__ = core.__all__

# XXX those should not be needed by the scons command only...
from core.extension import get_python_inc, get_pythonlib_dir

# XXX those are needed by the scons command only...
from core.misc import get_scons_path, get_scons_build_dir, \
                      get_scons_configres_dir, get_scons_configres_filename
#from core.libinfo import get_paths as scons_get_paths

# XXX those should not be needed by the scons command only...
from core.extension import get_python_inc, get_pythonlib_dir

# Those functions really belong to the public API
from core.helpers import GetNumpyEnvironment

import checkers
from checkers import *
__all__ += checkers.__all__

def get_version():
    import version
    return version.VERSION

def is_dev_version():
    import version
    return version.DEV

# XXX: this is ugly, better find the mathlibs with a checker 
# XXX: this had nothing to do here, too...
def scons_get_paths(paths):
    import os
    return paths.split(os.pathsep)

def scons_get_mathlib(env):
    from numscons.numdist import get_mathlibs
    path_list = scons_get_paths(env['include_bootstrap']) + [None]
    for i in path_list:
        try:
            mlib =  get_mathlibs(i)
            return mlib
        except IOError:
            pass
    raise RuntimeError("FIXME: no mlib found ?")
