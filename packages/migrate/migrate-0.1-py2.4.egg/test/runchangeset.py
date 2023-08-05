import fixture
from migrate.versioning.controlled import *
from migrate.versioning import script
import os,shutil

class RunChangeset(fixture.Pathed,fixture.DB):
    level=fixture.DB.CONNECT
    def setUp(self):
        Repository.clear()
        self.path_repos=self.tmp_repos()
        self.path_script=self.tmp_py()
        # Create repository, script
        Repository.create(self.path_repos,'repository_name')
    def test_changeset_run(self):
        """Running a changeset against a repository gives expected results"""
        repos=Repository(self.path_repos)
        for i in range(10):
            script.PythonFile.create(self.path_script)
            repos.commit(self.path_script)
        try:
            ControlledSchema(self.conn,repos).drop()
        except:
            pass
        db=ControlledSchema.create(self.conn,repos)

        # Scripts are empty; we'll check version # correctness.
        # (Correct application of their content is checked elsewhere)
        self.assertEquals(db.version,0)
        db.upgrade(1)
        self.assertEquals(db.version,1)
        db.upgrade(5)
        self.assertEquals(db.version,5)
        db.upgrade(5)
        self.assertEquals(db.version,5)
        db.upgrade(None) # Latest is implied
        self.assertEquals(db.version,10)
        self.assertRaises(Exception,db.upgrade,11)
        self.assertEquals(db.version,10)
        db.upgrade(9)
        self.assertEquals(db.version,9)
        db.upgrade(0)
        self.assertEquals(db.version,0)
        self.assertRaises(Exception,db.upgrade,-1)
        self.assertEquals(db.version,0)
        #changeset = repos.changeset(self.url,0)
        db.drop()

if __name__=='__main__':
    fixture.main()
