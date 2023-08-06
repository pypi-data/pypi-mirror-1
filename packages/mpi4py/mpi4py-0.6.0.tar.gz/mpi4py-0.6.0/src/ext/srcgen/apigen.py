#! /usr/bin/env python

# $Id$

import sys, os
from os.path import join, extsep, pardir
import re

if len(sys.argv) > 1 and  sys.argv[1] == '-o':
    outdir = sys.argv[2]
else:
    outdir = pardir
assert os.path.isdir(outdir)

mpiobjs = ['op',
           'win',
           'comm',
           'info',
           'file',
           'group',
           'status',
           'request',
           'datatype',
           'errhandler',
           ]
mpiobjs.sort()

fname,h,c  = 'object','h','c'
header_code = open(fname+extsep+h).read()
source_code = open(fname+extsep+c).read()

header_code = re.sub(r"<(\w+)>", r"%(\1)s", header_code)
source_code = re.sub(r"<(\w+)>", r"%(\1)s", source_code)

source_code = source_code.split('\n')
status_code = []
others_code = []
while len(source_code):
    line = source_code.pop(0)
    if '#if !defined(Py_MPISTATUSOBJECT_H)' not in line:
        status_code.append(line)
        others_code.append(line)
    else:
        line = source_code.pop(0)
        while '#else' not in line:
            others_code.append(line)
            line = source_code.pop(0)
        line = source_code.pop(0)
        while '#endif' not in line:
            status_code.append(line)
            line = source_code.pop(0)

status_code = '\n'.join(status_code)
others_code = '\n'.join(others_code)

object_h = []
object_c = []
for o in mpiobjs:
    obj = {'obj': o.lower(),
           'Obj': o.capitalize(),
           'OBJ': o.upper(),
           }
    if o.lower()=='status':
        object_h += [header_code % obj]
        object_c += [status_code % obj]
    else:
        object_h += [header_code % obj]
        object_c += [others_code % obj]
object_h = '\n'.join(object_h)
object_c = '\n'.join(object_c)


# --------------------------------------------------------------------

libmpi, h, c  = 'libmpi', 'h', 'c'

libmpi_h = open(join(libmpi+extsep+h)).read()
libmpi_c = open(join(libmpi+extsep+c)).read()

libmpi_h = libmpi_h.replace('<MPI_OBJECT_H>', object_h)
libmpi_c = libmpi_c.replace('<MPI_OBJECT_C>', object_c)

open(join(outdir, libmpi+extsep+h),'w').write(libmpi_h)
open(join(outdir, libmpi+extsep+c),'w').write(libmpi_c)

# --------------------------------------------------------------------
