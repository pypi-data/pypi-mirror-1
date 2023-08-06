import unittest
from mpi4py import MPI


class TestRequestNull(unittest.TestCase):

    def testFree(self):
        self.assertRaises(MPI.Exception, MPI.REQUEST_NULL.Free)

    def testCancel(self):
        self.assertRaises(MPI.Exception, MPI.REQUEST_NULL.Cancel)

    def testGetStatus(self):
        self.assertRaises(MPI.Exception, MPI.REQUEST_NULL.Get_status)


class TestRequest(unittest.TestCase):

    def setUp(self):
        self.REQUEST = MPI.Request()
        self.STATUS  = MPI.Status()

    def testFree(self):
        self.assertRaises(MPI.Exception, MPI.REQUEST_NULL.Free)

    def testCancel(self):
        self.assertRaises(MPI.Exception, MPI.REQUEST_NULL.Cancel)

    def testWait(self):
        self.REQUEST.Test()
        self.REQUEST.Test(None)
        self.REQUEST.Test(self.STATUS)

    def testTest(self):
        self.REQUEST.Wait()
        self.REQUEST.Wait(None)
        self.REQUEST.Test(self.STATUS)

class TestRequestArray(unittest.TestCase):

    def setUp(self):
        self.REQUESTS  = [MPI.Request() for i in range(5)]
        self.STATUSES  = [MPI.Status()  for i in range(5)]

    def testWaitany(self):
        MPI.Request.Waitany(self.REQUESTS)
        MPI.Request.Waitany(self.REQUESTS, None)
        MPI.Request.Waitany(self.REQUESTS, self.STATUSES[0])

    def testTestany(self):
        MPI.Request.Testany(self.REQUESTS)
        MPI.Request.Testany(self.REQUESTS, None)
        MPI.Request.Testany(self.REQUESTS, self.STATUSES[0])

    def testWaitall(self):
        MPI.Request.Waitall(self.REQUESTS)
        MPI.Request.Waitall(self.REQUESTS, None)
        MPI.Request.Waitall(self.REQUESTS, [])
        MPI.Request.Waitall(self.REQUESTS, self.STATUSES)

    def testTestall(self):
        MPI.Request.Testall(self.REQUESTS)
        MPI.Request.Testall(self.REQUESTS, None)
        MPI.Request.Testall(self.REQUESTS, [])
        MPI.Request.Testall(self.REQUESTS, self.STATUSES)

    def testWaitsome(self):
        out = (MPI.UNDEFINED, [])
        ret = MPI.Request.Waitsome(self.REQUESTS)
        self.assertEqual(ret, out)
        ret = MPI.Request.Waitsome(self.REQUESTS, None)
        self.assertEqual(ret, out)
        ret = MPI.Request.Waitsome(self.REQUESTS, [])
        self.assertEqual(ret, out)
        ret = MPI.Request.Waitsome(self.REQUESTS, self.STATUSES)
        self.assertEqual(ret, out)

    def testTestsome(self):
        out = (MPI.UNDEFINED, [])
        ret = MPI.Request.Testsome(self.REQUESTS)
        self.assertEqual(ret, out)
        ret = MPI.Request.Testsome(self.REQUESTS, None)
        self.assertEqual(ret, out)
        ret = MPI.Request.Testsome(self.REQUESTS, [])
        self.assertEqual(ret, out)
        ret = MPI.Request.Testsome(self.REQUESTS, self.STATUSES)
        self.assertEqual(ret, out)


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit:
        pass
