import unittest
from mpi4py import MPI


HAVE_INFO = True

class TestInfoNull(unittest.TestCase):

    def testTruth(self):
        if not HAVE_INFO: return
        self.assertFalse(bool(MPI.INFO_NULL))

    def testDup(self):
        if not HAVE_INFO: return
        INFO_NULL_Dup = lambda : MPI.INFO_NULL.Dup()
        self.assertRaises(MPI.Exception, INFO_NULL_Dup)

    def testFree(self):
        if not HAVE_INFO: return
        INFO_NULL_Free = lambda : MPI.INFO_NULL.Free()
        self.assertRaises(MPI.Exception, INFO_NULL_Free)

    def testGet(self):
        if not HAVE_INFO: return
        INFO_NULL_Get = lambda : MPI.INFO_NULL.Get('key')
        self.assertRaises(MPI.Exception, INFO_NULL_Get)

    def testSet(self):
        if not HAVE_INFO: return
        INFO_NULL_Set = lambda : MPI.INFO_NULL.Set('key', 'value')
        self.assertRaises(MPI.Exception, INFO_NULL_Set)

    def testDelete(self):
        if not HAVE_INFO: return
        INFO_NULL_Delete = lambda : MPI.INFO_NULL.Delete('key')
        self.assertRaises(MPI.Exception, INFO_NULL_Delete)

    def testGetNKeys(self):
        if not HAVE_INFO: return
        INFO_NULL_Get_nkeys = lambda : MPI.INFO_NULL.Get_nkeys()
        self.assertRaises(MPI.Exception, INFO_NULL_Get_nkeys)

    def testGetNthKey(self):
        if not HAVE_INFO: return
        INFO_NULL_Get_nthkey = lambda : MPI.INFO_NULL.Get_nthkey(0)
        self.assertRaises(MPI.Exception, INFO_NULL_Get_nthkey)

    def testMappingMethods(self):
        if not HAVE_INFO: return
        inull = MPI.INFO_NULL
        def getitem(): return inull['k']
        def setitem(): inull['k'] = 'v'
        def delitem(): del inull['k']
        self.assertEqual(len(inull), 0)
        self.assertRaises(KeyError, getitem)
        self.assertRaises(KeyError, setitem)
        self.assertRaises(KeyError, delitem)
        self.assertFalse('key' in inull)


class TestInfo(unittest.TestCase):

    def setUp(self):
        try:
            self.INFO  = MPI.Info.Create()
        except NotImplementedError:
            self.INFO = None
            global HAVE_INFO
            HAVE_INFO = False

    def tearDown(self):
        if not HAVE_INFO: return
        self.INFO.Free()
        self.assertEqual(self.INFO, MPI.INFO_NULL)

    def testTruth(self):
        if not HAVE_INFO: return
        self.assertFalse(bool(MPI.INFO_NULL))

    def testDup(self):
        if not HAVE_INFO: return
        info = self.INFO.Dup()
        self.assertNotEqual(self.INFO, info)
        self.assertEqual(info.Get_nkeys(), 0)
        info2 = MPI.Info(info)
        self.assertTrue(info is info2)
        info.Free()
        self.assertFalse(info)
        self.assertFalse(info2)

    def testGet(self):
        if not HAVE_INFO: return
        value, flag = self.INFO.Get('key')
        self.assertEqual(value, None)
        self.assertEqual(flag,  False)

    def testGetNKeys(self):
        if not HAVE_INFO: return
        self.assertEqual(self.INFO.Get_nkeys(), 0)

    def testGetSetDelete(self):
        if not HAVE_INFO: return
        INFO = self.INFO
        self.assertEqual(INFO.Get_nkeys(), 0)
        INFO.Set('key', 'value')
        nkeys = INFO.Get_nkeys()
        self.assertEqual(nkeys, 1)
        key = INFO.Get_nthkey(0)
        self.assertEqual(key, 'key')
        value, flag = INFO.Get('key')
        self.assertEqual(value, 'value')
        self.assertEqual(flag,  True)
        INFO.Delete('key')
        nkeys = INFO.Get_nkeys()
        self.assertEqual(nkeys, 0)
        value, flag = INFO.Get('key')
        self.assertEqual(value, None)
        self.assertEqual(flag,  False)
        del_key = lambda : INFO.Delete('key')
        self.assertRaises(MPI.Exception, del_key)
        get_nthkey = lambda : INFO.Get_nthkey(0)
        self.assertRaises(MPI.Exception, get_nthkey)

    def testPyMethods(self):
        if not HAVE_INFO: return
        INFO = self.INFO
        self.assertEqual(len(INFO), 0)
        self.assertTrue('key' not in INFO)
        INFO['key'] = 'value'
        self.assertTrue('key' in INFO)
        self.assertEqual(len(INFO), 1)
        self.assertEqual(INFO['key'], 'value')
        for key in INFO:
            pass
        self.assertEqual(key, 'key')
        del INFO['key']
        self.assertTrue('key' not in INFO)
        self.assertEqual(len(INFO), 0)
        getitem = lambda : INFO['key']
        self.assertRaises(KeyError, getitem)
        def delitem(): del INFO['key']
        self.assertRaises(MPI.Exception, delitem)


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit:
        pass
