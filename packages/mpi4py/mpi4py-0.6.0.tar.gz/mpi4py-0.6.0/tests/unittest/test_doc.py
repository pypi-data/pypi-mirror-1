import types
import unittest
from mpi4py import MPI


def getdoc(mc, docstrings):
    name = getattr(mc, '__name__', '<no-name>')
    doc = getattr(mc, '__doc__', None)
    docstrings[name] = doc
    for k, v in vars(mc).items():
        if type(v) is types.FunctionType:
            getdoc(v, docstrings)
        elif isinstance(v, types.TypeType) or type(v) is types.ClassType:
            getdoc(v, docstrings)

class TestDoc(unittest.TestCase):

    def testDoc(self):
        docs = { }
        getdoc(MPI, docs)
        for k in docs:
            if not k.endswith('__'):
                doc = docs[k]
                self.assertTrue(doc.strip())


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit:
        pass
