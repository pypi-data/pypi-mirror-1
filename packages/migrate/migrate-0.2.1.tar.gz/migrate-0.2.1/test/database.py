from sqlalchemy import *
import fixture

# TODO: we'll need to have a way to run these tests on multiple databases. 

class ConnectTest(fixture.DB):
    level=fixture.DB.TXN
    def test_connect(self):
        """Connect to the database successfully"""
        # Connection is done in fixture.DB setup; make sure we can do stuff
        select(['42'],engine=self.engine).execute()

if __name__=='__main__':
    fixture.main()
