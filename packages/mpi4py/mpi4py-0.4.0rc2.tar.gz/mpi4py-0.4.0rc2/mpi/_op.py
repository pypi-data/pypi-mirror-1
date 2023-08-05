# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Revision:  $Revision: 1.15 $
# Date:      $Date: 2006/10/09 21:05:38 $
# Copyright: This file has been placed in the public domain.

"""
MPI Operations.
"""

__author__    = 'Lisandro Dalcin'
__credits__   = 'MPI Forum, MPICH Team, Open MPI Team.'
__date__      = '13 Oct 2006'
__version__   = '0.4.0'
__revision__  = '$Id: _op.py,v 1.15 2006/10/09 21:05:38 dalcinl Exp $'


def MAX(x, y):
    """maximum"""
    return max(x, y)

def MIN(x, y):
    """minimum"""
    return min(x, y)

def SUM(x, y):
    """sum"""
    return x + y

def PROD(x, y):
    """product"""
    return x * y

def BAND(x, y):
    """bit-wise and"""
    return x & y

def BOR(x, y):
    """bit-wise or"""
    return x | y
    
def BXOR(x, y):
    """bit-wise xor"""
    return x ^ y

def LAND(x, y):
    """logical and"""
    return bool(x) & bool(y)

def LOR(x, y):
    """logical or"""
    return bool(x) | bool(y)

def LXOR(x, y):
    """logical xor"""
    return bool(x) ^ bool(y)

def MAXLOC(x, y):
    """maximum and location"""
    u, i = x
    v, j = y
    w = max(u, v)
    if u == v:
        k = min(i, j)
    elif u <  v:
        k = j
    else:
        k = i
    return (w, k)

def MINLOC(x, y):
    """minimum and location"""
    u, i = x
    v, j = y
    w = min(u, v)
    if u == v:
        k = min(i, j)
    elif u <  v:
        k = i
    else:
        k = j
    return (w, k)

def REPLACE(x, y):
    """replace,  op(x, y) -> x"""
    return x
