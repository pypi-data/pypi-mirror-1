import unittest
from mpi4py import MPI


class TestErrors(unittest.TestCase):

    errorclasses = [item[1] for item in vars(MPI).items()
                    if item[0].startswith('ERR_')]
    errorclasses.insert(0, MPI.SUCCESS)
    errorclasses.remove(MPI.ERR_LASTCODE)

    def testGetErrorClass(self):
        for ierr in self.errorclasses:
            errcls = MPI.Get_error_class(ierr)
            self.assertTrue(errcls >= MPI.SUCCESS)
            self.assertTrue(errcls < MPI.ERR_LASTCODE)
            self.assertEqual(errcls, ierr)

    def testGetErrorStrings(self):
        for ierr in self.errorclasses:
            errstr = MPI.Get_error_string(ierr)

    def testException(self):
        for ierr in self.errorclasses:
            errstr = MPI.Get_error_string(ierr)
            errcls = MPI.Get_error_class(ierr)
            errexc = MPI.Exception(ierr)
            #self.assertEqual(errexc.error_code,  ierr)
            #self.assertEqual(errexc.error_class, ierr)
            #self.assertEqual(errexc.error_string, errstr)
            self.assertEqual(str(errexc), errstr)
            self.assertEqual(int(errexc), ierr)
            self.assertTrue(errexc == ierr)
            self.assertTrue(errexc == errexc)
            self.assertFalse(errexc != ierr)
            self.assertFalse(errexc != errexc)



class TestErrhandler(unittest.TestCase):

    def testPredefined(self):
        self.assertFalse(MPI.ERRHANDLER_NULL)
        self.assertTrue(MPI.ERRORS_ARE_FATAL)
        self.assertTrue(MPI.ERRORS_RETURN)
        self.assertRaises(MPI.Exception, MPI.ERRHANDLER_NULL.Free)
        #self.assertRaises(MPI.Exception, MPI.ERRORS_ARE_FATAL.Free)
        #self.assertRaises(MPI.Exception, MPI.ERRORS_RETURN.Free)

    def testCommGetSetErrhandler(self):
        set_null_eh = lambda : MPI.COMM_WORLD.Set_errhandler(MPI.ERRHANDLER_NULL)
        self.assertRaises(MPI.Exception, set_null_eh)
        for ERRHANDLER in [MPI.ERRORS_ARE_FATAL, MPI.ERRORS_RETURN,
                           MPI.ERRORS_ARE_FATAL, MPI.ERRORS_RETURN,]:
            errhdl_1 = MPI.COMM_WORLD.Get_errhandler()
            self.assertNotEqual(errhdl_1, MPI.ERRHANDLER_NULL)
            MPI.COMM_WORLD.Set_errhandler(ERRHANDLER)
            errhdl_2 = MPI.COMM_WORLD.Get_errhandler()
            self.assertEqual(errhdl_2, ERRHANDLER)
            errhdl_2.Free()
            self.assertEqual(errhdl_2, MPI.ERRHANDLER_NULL)
            #continue
            MPI.COMM_WORLD.Set_errhandler(errhdl_1)
            errhdl_1.Free()
            self.assertEqual(errhdl_1, MPI.ERRHANDLER_NULL)

    def testGetErrhandler(self):
        errhdls = []
        for i in range(100):
            e = MPI.COMM_WORLD.Get_errhandler()
            errhdls.append(e)
        for e in errhdls:
            e.Free()

if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit:
        pass
