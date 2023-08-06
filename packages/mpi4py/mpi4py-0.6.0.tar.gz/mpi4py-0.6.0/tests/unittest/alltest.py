import sys, os

import unittest
if sys.version_info < (2,4):
    unittest.TestCase.assertTrue  = unittest.TestCase.failUnless
    unittest.TestCase.assertFalse = unittest.TestCase.failIf

try:
    from mpi4py import MPI
except:
    from distutils.util import get_platform
    plat_specifier = ".%s-%s" % (get_platform(), sys.version[0:3])
    os.path.split(__file__)[0]
    path = os.path.join(os.path.split(__file__)[0],
                        os.path.pardir, os.path.pardir,
                        'build', 'lib' + plat_specifier)
    sys.path.append(path)
    from mpi4py import MPI

def test_cases(exclude=()):
    from glob import glob
    directory = os.path.split(__file__)[0]
    pattern = os.path.join(directory, 'test_*.py')
    test_list = []
    for test_file in glob(pattern):
        filename = os.path.basename(test_file)
        modulename = os.path.splitext(filename)[0]
        if modulename not in exclude:
            test = __import__(modulename)
            test_list.append(test)
    return test_list

for test in test_cases(exclude=['test_spawn',
                                ]):
    try:
        unittest.main(test)
    except SystemExit:
        pass
