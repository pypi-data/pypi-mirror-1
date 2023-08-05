import unittest
from string import split
from base64 import urlsafe_b64decode, urlsafe_b64encode

def encodePKString(ids):
    """ encode the tuple of PrimaryKeys
        into a dataset of the following structure
        (1,'klaus') --> int:1;str:klaus; """
    pkstring=""
    for key in ids:
        if isinstance(key, int):
	    pkstring += "int:%i;" %key
	elif isinstance(key, str):
	    pkstring += "str:%s;" %key
    return urlsafe_b64encode(pkstring)

def decodePKString(s):
    """ docode the PrimaryKey String back
        into the tuple
        int:1;str:klaus; --> (1,'klaus') """
    s = urlsafe_b64decode(str(s))
    if s.endswith(';'):
        s=s[:-1]
    rc=[]
    for key in split(s,';'):
        typ, value = split(key,':')
        if typ == 'int':
		    rc.append(int(value))
        elif typ == 'str':
		    rc.append(str(value))
    return tuple(rc)

#class Utils(unittest.TestCase):
#    ids = (1,'klaus')
#    string = "int:1;str:klaus;"
#	
#    def test_encodePKString(self):
#        self.assertEqual(encodePKString(self.ids), self.string)
#    
 #   def test_decodePKString(self):
##		self.assertEqual(decodePKString(self.string), self.ids)
#
#if __name__ == "__main__":
#	unittest.main()
