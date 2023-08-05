import unittest

class Base(unittest.TestCase):
    """Base class for other test cases"""
    def ignoreErrors(self,*p,**k):
        """Call a function, ignoring any exceptions"""
        func=p[0]
        try:
            func(*p[1:],**k)
        except:
            pass
