import unittest
from mpi4py import MPI

class TestStatus(unittest.TestCase):

    def setUp(self):
        self.STATUS = MPI.Status()

    def testDefaultFieldValues(self):
        self.assertEqual(self.STATUS.Get_source(), MPI.ANY_SOURCE)
        self.assertEqual(self.STATUS.Get_tag(),    MPI.ANY_TAG)
        self.assertEqual(self.STATUS.Get_error(),  MPI.SUCCESS)

    def testProperties(self):
        self.assertEqual(self.STATUS.Get_source(), self.STATUS.source)
        self.assertEqual(self.STATUS.Get_tag(),    self.STATUS.tag)
        self.assertEqual(self.STATUS.Get_error(),  self.STATUS.error)
        self.STATUS.source = 0
        self.STATUS.tag    = 0
        self.STATUS.error  = MPI.SUCCESS
        self.assertEqual(self.STATUS.source, 0)
        self.assertEqual(self.STATUS.tag,    0)
        self.assertEqual(self.STATUS.error,  MPI.SUCCESS)

    def testGetCount(self):
        count = self.STATUS.Get_count()
        self.assertEqual(count, 0)

    def testGetElements(self):
        elements = self.STATUS.Get_elements()
        self.assertEqual(elements, 0)

    def testIsCancelled(self):
        self.STATUS.Is_cancelled()


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit:
        pass
