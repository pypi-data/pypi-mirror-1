import unittest
from mpi4py import MPI
import array

obj = [None,
       True,
       False,
       7,
       3.14,
       1+2j,
       'qwerty']

chrbuf = array.array('c', '\0' * 1000)

pickle = [MPI.Pickle, MPI.Pickle(0), MPI.Pickle(1), MPI.Pickle(2)]
marshal = [MPI.Marshal, MPI.Marshal(0), MPI.Marshal(1)]

class TestSerial(unittest.TestCase):

    def _test(self, obj, serializers):
        for SERIAL in serializers:
            s = SERIAL.dump(obj)
            SERIAL.dump(obj, chrbuf)
            assert s == chrbuf[:len(s)].tostring()
            assert obj == SERIAL.load(s)
            assert obj == SERIAL.load(chrbuf)
    
    def testPickle(self):
        self._test(obj, pickle)
        for o in obj:
            self._test(o, pickle)
        
    def testMarshal(self):
        self._test(obj, marshal)
        for o in obj:
            self._test(o, marshal)
        

if __name__ == '__main__':
    #unittest.main()
    try:
        unittest.main()
    except SystemExit:
        pass
