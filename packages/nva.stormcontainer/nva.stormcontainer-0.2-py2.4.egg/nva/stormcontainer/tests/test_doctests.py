import unittest
from zope.testing import doctest
from storm.locals import *

class Person(object):
    __storm_table__ = "person"

    id = Int(primary=True)
    name = Unicode()

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
			     package="nva.stormcontainer",
                             optionflags=doctest.ELLIPSIS),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
