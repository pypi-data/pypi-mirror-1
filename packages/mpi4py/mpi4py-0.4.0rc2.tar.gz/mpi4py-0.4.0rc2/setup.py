#!/bin/env python
# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Revision:  $Revision: 1.26 $
# Date:      $Date: 2006/11/05 01:39:21 $
# Copyright: This script has been placed in the public domain.

"""
MPI for Python
==============

This package provides MPI support for Python scripting in parallel
environments. It is constructed on top of the MPI-1/MPI-2
specification, but provides an object oriented interface which closely
follows MPI-2 C++ bindings.

This module supports point-to-point (sends, receives) and collective
(broadcasts, scatters, gathers, reductions) communications of any
*picklable* Python object.

For objects exporting single-segment buffer interface (strings, NumPy
arrays, etc.), blocking/nonbloking/persistent point-to-point,
collective and one-sided (put, get, accumulate) communications are
fully supported, as well as parallel I/O (blocking and nonbloking,
collective and noncollective read and write operatios using explicit
file offsets, individual file pointers and shared file pointers).

There is also full support for group and communicator (inter, intra,
cartesian and graph topologies) creation and management, as well as
any native or user-defined datatypes.
"""

# --------------------------------------------------------------------
# Metadata
# --------------------------------------------------------------------

name    = 'mpi4py'
version = file('VERSION.txt').read().strip()
descr   = __doc__.split('\n')[1:-1]; del descr[1:3]
devstat  = ['Development Status :: 5 - Production/Stable']
download = 'http://cheeseshop.python.org/packages/source/m/mpi4py/%s-%s.tar.gz'

classifiers = """
License :: Public Domain
Operating System :: POSIX
Intended Audience :: Developers
Intended Audience :: Science/Research
Programming Language :: C
Programming Language :: C++
Programming Language :: Python
Topic :: Scientific/Engineering
Topic :: Software Development :: Libraries :: Python Modules
"""

keywords = """
scientific computing
parallel computing
message passing
MPI
"""

metadata = {             
    'name'             : name,
    'version'          : version,
    'description'      : descr.pop(0),
    'long_description' : '\n'.join(descr),
    #'download_url'     : download % (name, version),
    'author'           : 'Lisandro Dalcin',
    'author_email'     : 'dalcinl@users.sourceforge.net',
    'classifiers'      : [c for c in classifiers.split('\n') if c],
    'keywords'         : [k for k in keywords.split('\n')    if k],
    'license'          : 'Public Domain',
    'maintainer'       : 'Lisandro Dalcin',
    'maintainer_email' : 'dalcinl@users.sourceforge.net',
    'platforms'        : ['POSIX'],
    'url'              : 'http://mpi4py.scipy.org/',
    }
metadata['classifiers'] += devstat

del name, version, descr, devstat, download

# --------------------------------------------------------------------
# Extension modules
# --------------------------------------------------------------------

def ext_modules():
    # MPI types and C API module
    libmpi = dict(name='mpi4py.libmpi',
                  sources=['mpi/ext/libmpi.c'],
                  depends=['mpi/ext/libmpi.h'])
    # MPI extension module
    mpi = dict(name='mpi4py._mpi',
               sources=['mpi/ext/mpi.c'],
               depends=['mpi/ext/libmpi.h',
                        'mpi/ext/config.h',
                        'mpi/ext/compat.h',
                        'mpi/ext/macros.h',])
    # Pickle support
    pickle = dict(name='mpi4py._pickle',
                  sources=['mpi/ext/pickle.c'])
    # Marshal support
    marshal = dict(name='mpi4py._marshal',
                   sources=['mpi/ext/marshal.c'])
    # SWIG support
    mpi_swig = dict(name='mpi4py._mpi_swig',
                    sources=['mpi/ext/mpi_swig.c'],
                    depends=['mpi/ext/libmpi.h'])
    # return all extensions
    return [libmpi, mpi, mpi_swig, pickle, marshal]

def headers():
    return ['mpi/ext/libmpi.h']

def executables():
    pyexe = dict(name='mpi4py',
                 sources=['mpi/exe/python.c'])
    return [pyexe]


# --------------------------------------------------------------------
# Setup
# --------------------------------------------------------------------

from distutils.core import setup
from mpidistutils import Distribution, Extension, Executable
from mpidistutils import config, build, build_ext
from mpidistutils import build_exe, install_exe, clean_exe
LibHeader = lambda header: str(header)
ExtModule = lambda extension: Extension(**extension)
ExeBinary = lambda executable: Executable(**executable)
        
def main():
    """
    distutils.setup(*targs, **kwargs)
    """
    setup(packages = ['mpi4py'],
          package_dir = {'mpi4py' : 'mpi'},
          headers = [LibHeader(hdr) for hdr in headers()],
          ext_modules = [ExtModule(ext) for ext in ext_modules()],
          executables = [ExeBinary(exe) for exe in executables()],
          distclass = Distribution,
          cmdclass = {'config'      : config,
                      'build'       : build,
                      'build_ext'   : build_ext,
                      'build_exe'   : build_exe,
                      'clean_exe'   : clean_exe,
                      'install_exe' : install_exe,
                      },
          **metadata)
    
if __name__ == '__main__':
    # hack distutils.sysconfig to eliminate debug flags
    from distutils import sysconfig
    cvars = sysconfig.get_config_vars()
    cflags = cvars.get('OPT')
    if cflags:
        cflags = cflags.split()
        for flag in ('-g', '-g3'):
            if flag in cflags:
                cflags.remove(flag)
        cvars['OPT'] = str.join(' ', cflags) 
    # and now call main
    main()

# --------------------------------------------------------------------
