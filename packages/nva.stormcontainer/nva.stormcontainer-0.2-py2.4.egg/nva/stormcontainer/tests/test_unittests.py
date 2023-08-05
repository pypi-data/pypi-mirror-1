import unittest
from nva.stormcontainer.utils import *
from base64 import urlsafe_b64encode
from base64 import urlsafe_b64decode

class TestUtils(unittest.TestCase):
    ids = (1,'klaus')
    string = "int:1;str:klaus;"
    encode_string = urlsafe_b64encode(string)


    oneids = (5,)
    onestring = "int:5;"
    oneencode_string = urlsafe_b64encode(onestring)


    def test_encodePKString(self):
        self.assertEqual(encodePKString(self.ids), self.encode_string)

    def test_decodePKString(self):
        self.assertEqual(decodePKString(self.encode_string), self.ids)

    def test_oneencodePKString(self):
        self.assertEqual(encodePKString(self.oneids), self.oneencode_string)

    def test_onedecodePKString(self):
        self.assertEqual(decodePKString(self.oneencode_string), self.oneids)



def test_suite():
    return unittest.TestSuite( unittest.makeSuite(TestUtils),)

if __name__ == "__main__":
        unittest.main()

