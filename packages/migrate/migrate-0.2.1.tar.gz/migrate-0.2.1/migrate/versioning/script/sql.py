from script import *

class SqlFile(ScriptFile):
    """A file containing plain SQL statements."""
    def __init__(self,path):
        super(SqlFile,self).__init__(path)
        file = open(path)
        self.text = file.read()
        file.close()

    def run(self,engine,step):
        sqlalchemy.text(self.text,engine=engine).execute()
