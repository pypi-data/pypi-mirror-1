import fixture
from migrate.versioning import logengine
from migrate.versioning.script import *
from migrate.versioning import exceptions
import os,shutil

class PyTests(fixture.Pathed):
    def test_create(self):
        """We can create a migration script"""
        path=self.tmp_py()
        # Creating a file that doesn't exist should succeed
        PythonFile.create(path)
        self.assert_(os.path.exists(path))
        # Created file should be a valid script (If not, raises an error)
        PythonFile.verify(path)
        # Can't create it again: it already exists
        self.assertRaises(exceptions.PathFoundError,PythonFile.create,path)

    def test_verify_notfound(self):
        """Correctly verify a python migration script: nonexistant file"""
        path=self.tmp_py()
        self.assert_(not os.path.exists(path))
        # Fails on empty path
        self.assertRaises(exceptions.InvalidScriptError,PythonFile.verify,path)
        self.assertRaises(exceptions.InvalidScriptError,PythonFile,path)

    def test_verify_invalidpy(self):
        """Correctly verify a python migration script: invalid python file"""
        path=self.tmp_py()
        # Create empty file
        f=open(path,'w')
        f.write("def fail")
        f.close()
        self.assertRaises(Exception,PythonFile.verify_module,path)
        # script isn't verified on creation, but on module reference
        py = PythonFile(path)
        self.assertRaises(Exception,(lambda x: x.module),py)

    def test_verify_nofuncs(self):
        """Correctly verify a python migration script: valid python file; no upgrade func"""
        path=self.tmp_py()
        # Create empty file
        f=open(path,'w')
        f.write("def zergling():\n\tprint 'rush'")
        f.close()
        self.assertRaises(exceptions.InvalidScriptError,PythonFile.verify_module,path)
        # script isn't verified on creation, but on module reference
        py = PythonFile(path)
        self.assertRaises(exceptions.InvalidScriptError,(lambda x: x.module),py)

    def test_verify_success(self):
        """Correctly verify a python migration script: success"""
        path=self.tmp_py()
        # Succeeds after creating
        PythonFile.create(path)
        PythonFile.verify(path)
    
    def test_compile(self):
        """Compiling a Python script to logsql files should work"""
        path=self.tmp_py()
        PythonFile.create(path,logsql=True)
        py = PythonFile(path)
        # Fails: invalid op
        self.assertRaises(exceptions.ScriptError,py.compile,'postgres','fgsfds')
        # Fails: invalid db
        self.assertRaises(exceptions.ScriptError,py.compile,'fgsfds','upgrade')
        # Should succeed, and return a logengine.SqlLog
        item=py.compile('postgres','upgrade')
        self.assert_(isinstance(item,logengine.SqlLog))
        # Should succeed, write a file, and return a script.logsql file object
        item=py.compile('postgres','downgrade',self.tmp())
        self.assert_(isinstance(item,LogsqlFile))
        self.assert_(os.path.exists(item.path))

if __name__=='__main__':
    fixture.main()
