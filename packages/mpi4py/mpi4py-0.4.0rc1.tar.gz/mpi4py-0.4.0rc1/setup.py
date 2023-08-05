#!/bin/env python
# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Revision:  $Revision: 1.23 $
# Date:      $Date: 2006/10/13 15:48:40 $
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
download = 'http://www.cimec.org.ar/python/%s-%s.tar.gz'

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
    'url'              : 'http://www.cimec.org.ar/python',
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
    # SWIG support
    mpi_swig = dict(name='mpi4py._mpi_swig',
                    sources=['mpi/ext/mpi_swig.c'],
                    depends=['mpi/ext/libmpi.h'])
    # Pickle support
    pickle = dict(name='mpi4py._pickle',
                  sources=['mpi/ext/pickle.c'])
    # Marshal support
    marshal = dict(name='mpi4py._marshal',
                   sources=['mpi/ext/marshal.c'])

    # return all extensions
    return [libmpi, mpi, mpi_swig, pickle, marshal]

def ext_headers():
    return ['mpi/ext/libmpi.h']


# --------------------------------------------------------------------
# Setup
# --------------------------------------------------------------------

from distutils.core import setup, Extension
from mpidistutils import config, build, build_ext
ExtModule = lambda extension: Extension(**extension)
ExtHeader = lambda header: str(header)
        
def main():
    """
    distutils.setup(*targs, **kwargs)
    """
    setup(packages = ['mpi4py'],
          package_dir = {'mpi4py' : 'mpi'},
          ext_modules = [ExtModule(e) for e in ext_modules()],
          headers = [ExtHeader(h) for h in ext_headers()],
          cmdclass = {'config'    : config,
                      'build'     : build,
                      'build_ext' : build_ext},
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
