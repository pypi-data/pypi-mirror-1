from pathed import *
import os
import shutil
import sys

class Shell(Pathed):
    """Base class for command line tests"""
    def execute(self,command,*p,**k):
        """Return the fd of a command; can get output (stdout/err) and exitcode"""
        # We might be passed a file descriptor for some reason; if so, just return it
        if type(command) is file:
            return command
        # Redirect stderr to stdout
        # This is a bit of a hack, but I've not found a better way
        fd=os.popen(command+' 2>&1',*p,**k)
        return fd
    def exitcode(self,*p,**k):
        """Execute a command and return its exit code
        ...without printing its output/errors
        """
        key='emit'
        emit = k.pop(key,False)
        fd=self.execute(*p,**k)
        result = fd.read()
        if emit:
            print result
        return fd.close()

    def assertFailure(self,*p,**k):
        self.assert_(self.exitcode(*p,**k))
    def assertSuccess(self,*p,**k):
        self.assert_(not self.exitcode(*p,**k))
