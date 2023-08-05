import sys, glob
import unittest
from mpi4py import MPI

if sys.version_info < (2,4):
    unittest.TestCase.assertTrue  = unittest.TestCase.failUnless
    unittest.TestCase.assertFalse = unittest.TestCase.failIf
    
test_cases = []
for filename in glob.glob('test_*.py'):
    name = filename.split('.')[0]
    test = __import__(name)
    test_cases.append(test)

for test in test_cases:
    try:
        unittest.main(test, argv=['-q'])
    except SystemExit:
        pass
