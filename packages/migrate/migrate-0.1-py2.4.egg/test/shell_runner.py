import fixture
from migrate.versioning import shell
from migrate.versioning import api

class testOptions(fixture.Base):
    def test_to_dict(self):
        """opts convert to dictionaries correctly"""
        opts=shell.OptionValues()
        setattr(opts,'test','test')
        setattr(opts,'test2',True)
        setattr(opts,'test3',None)
        expected=dict(test='test',test2=True,test3=None)
        self.assertEquals(opts.to_dict(),expected)
        del expected['test3']
        self.assertEquals(opts.to_dict(purge_none=True),expected)
    def test_from_dict(self):
        """opts convert from dictionaries correctly"""
        values=dict(test='test',test2=True)
        opts=shell.OptionValues().from_dict(values)
        self.assertEquals(opts.to_dict(),values)
        self.assert_(opts.keys(),values.keys())
    

if __name__=='__main__':
    fixture.main()
