from script import *
from migrate.versioning import logengine

class LogsqlFile(ScriptFile):
    """A file containing a log of SQLAlchemy statements"""
    # logengine.SqlLog covers most things here; this is a wrapper
    def __init__(self,path):
        super(LogsqlFile,self).__init__(path)
        self.log = logengine.SqlLog.load(path)

    @classmethod
    def create(cls,log,path):
        """Save a given log to a file"""
        cls.require_notfound(path)
        log.write(path)
        ret = cls(path)
        return ret
    
    def run(self,*p,**k):
        return self.log.run(*p,**k)
