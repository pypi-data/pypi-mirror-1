#! /usr/bin/env python
# Author:    Lisandro Dalcin
# Contact:   dalcinl@gmail.com
# Copyright: This script has been placed in the public domain.
# Id:        $Id: setup.py 160 2007-12-13 18:51:48Z dalcinl $

"""
MPI for Python
==============

This package provides MPI support for Python scripting in parallel
environments. It is constructed on top of the MPI-1/MPI-2
specification, but provides an object oriented interface which closely
follows the MPI-2 C++ bindings.

This module supports point-to-point (send, receive) and collective
(broadcast, scatter, gather, reduction) communications of any
*picklable* Python object.

For objects exporting single-segment buffer interface (strings, NumPy
arrays, etc.), blocking/nonbloking/persistent point-to-point,
collective and one-sided (put, get, accumulate) communications are
fully supported, as well as parallel I/O (blocking and nonbloking,
collective and noncollective read and write operations using explicit
file offsets, individual file pointers and shared file
pointers).

There is also full support for group and communicator (inter, intra,
Cartesian and graph topologies) creation and management, as well as
creating user-defined datatypes. Additionally, there is almost
complete support for dynamic process creation and management (spawn,
name publishing).
"""

# --------------------------------------------------------------------
# Metadata
# --------------------------------------------------------------------

name     = 'mpi4py'
version  = open('VERSION.txt').read().strip()
descr    = __doc__.split('\n')[1:-1]; del descr[1:3]
devstat  = ['Development Status :: 5 - Production/Stable']
download = 'http://pypi.python.org/packages/source/%s/%s/%s-%s.tar.gz'

classifiers = """
License :: Public Domain
Operating System :: POSIX
Operating System :: Unix
Operating System :: MacOS
Operating System :: Microsoft :: Windows
Intended Audience :: Developers
Intended Audience :: Science/Research
Programming Language :: C
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

platforms = """
Linux
Unix
Mac OS-X
Windows
"""

metadata = {
    'name'             : name,
    'version'          : version,
    'description'      : descr.pop(0),
    'long_description' : '\n'.join(descr),
    'url'              : 'http://mpi4py.scipy.org/',
    'download_url'     : download % (name[0], name, name, version),
    'classifiers'      : [c for c in classifiers.split('\n') if c],
    'keywords'         : [k for k in keywords.split('\n')    if k],
    'platforms'        : [p for p in platforms.split('\n')   if p],
    'provides'         : ['mpi4py', 'mpi4py.MPI', 'mpi4py.libmpi'],
    'requires'         : ['pickle'],
    'license'          : 'Public Domain',
    'author'           : 'Lisandro Dalcin',
    'author_email'     : 'dalcinl@gmail.com',
    'maintainer'       : 'Lisandro Dalcin',
    'maintainer_email' : 'dalcinl@gmail.com',
    }
metadata['classifiers'] += devstat

del name, version, descr, devstat, download

# --------------------------------------------------------------------
# Extension modules
# --------------------------------------------------------------------

def ext_modules():
    import sys
    # MPI types and C API module
    libmpi = dict(name='mpi4py.libmpi',
                  sources=['src/ext/libmpi.c'],
                  depends=['src/ext/libmpi.h'])
    # MPI extension module
    mpi = dict(name='mpi4py._mpi',
               sources=['src/ext/mpi.c'],
               depends=['src/ext/libmpi.h',
                        'src/ext/config.h',
                        'src/ext/compat.h',
                        'src/ext/macros.h',
                        'src/ext/fastdefs.h',])
    # Pickle support
    pickle = dict(name='mpi4py._pickle',
                  sources=['src/ext/pickle.c'])
    # Marshal support
    marshal = dict(name='mpi4py._marshal',
                   sources=['src/ext/marshal.c'])
    # SWIG support
    mpi_swig = dict(name='mpi4py._mpi_swig',
                    sources=['src/ext/mpi_swig.c'],
                    depends=['src/ext/libmpi.h'])
    # return all extensions
    allext = [libmpi, mpi, pickle, marshal, mpi_swig]
    # SWIG is not ready for Py3k
    if sys.version_info >= (3,0): del allext[-1]
    return allext

def headers():
    return ['src/ext/libmpi.h']

def executables():
    import sys, os
    from distutils import sysconfig
    comp_args = []
    libraries = []
    library_dirs = []
    link_args = []
    if not sys.platform.startswith('win'):
        py_version = sysconfig.get_python_version()
        cfgDict = sysconfig.get_config_vars()
        if '-pthread' in cfgDict.get('CC', ''):
            comp_args.append('-pthread')
        libraries = ['python' + py_version]
        for var in ('LIBDIR', 'LIBPL'):
            library_dirs += cfgDict.get(var, '').split()
        for var in ('LIBS', 'MODLIBS', 'SYSLIBS', 'LDLAST',):
            link_args += cfgDict.get(var, '').split()
    pyexe = dict(name='mpi4py',
                 sources=['src/exe/python.c'],
                 libraries=libraries,
                 library_dirs=library_dirs,
                 extra_compile_args=comp_args,
                 extra_link_args=link_args)
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
          package_dir = {'mpi4py' : 'src'},
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
