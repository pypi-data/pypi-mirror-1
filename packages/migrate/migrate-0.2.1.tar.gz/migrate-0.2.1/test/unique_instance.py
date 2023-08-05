import fixture
from migrate.versioning.unique_instance import *

class UniqueInstanceTest(fixture.Base):
    def test_unique(self):
        """UniqueInstance should produce unique object instances"""
        class Uniq1(UniqueInstance):
            @classmethod
            def _key(cls,key):
                return str(key)
            def __init__(self,value):
                self.value=value
        class Uniq2(UniqueInstance):
            @classmethod
            def _key(cls,key):
                return str(key)
            def __init__(self,value):
                self.value=value
        
        a10 = Uniq1('a')

        # Different key: different instance
        b10 = Uniq1('b')
        self.assert_(a10 is not b10)

        # Different class: different instance
        a20 = Uniq2('a')
        self.assert_(a10 is not a20)

        # Same key/class: same instance
        a11 = Uniq1('a')
        self.assert_(a10 is a11)

        # __init__ is called
        self.assertEquals(a10.value,'a')

        # clear() causes us to forget all existing instances
        Uniq1.clear()
        a12 = Uniq1('a')
        self.assert_(a10 is not a12)
    
if __name__=='__main__':
    fixture.main()
