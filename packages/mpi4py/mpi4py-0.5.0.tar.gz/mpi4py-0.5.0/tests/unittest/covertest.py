import coverage
coverage = coverage.the_coverage

coverage.erase()
coverage.use_cache(0)
coverage.start()

coverage.exclude('"""')

coverage.exclude('def Buffer')

coverage.exclude('def Init')
coverage.exclude('def Init_thread')
coverage.exclude('def Finalize')
coverage.exclude('def Abort')

coverage.exclude('class Win')

coverage.exclude('_mpi_init')
coverage.exclude('_mpi_finalize')
coverage.exclude('SWIG')
coverage.exclude('_distribute')
coverage.exclude('_pprint')
coverage.exclude('_rprint')

import glob
import unittest
from mpi4py import MPI

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


coverage.stop()
#coverage.analysis(MPI)
coverage.report([MPI], show_missing=1)
coverage.annotate([MPI], directory='.')
