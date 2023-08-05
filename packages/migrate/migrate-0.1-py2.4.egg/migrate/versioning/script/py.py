from script import *
from logsql import LogsqlFile
from migrate.versioning.template import template
from migrate import run
from sqlalchemy import exceptions

class PythonFile(ScriptFile):
    def __init__(self,path):
        super(PythonFile,self).__init__(path)
        #self.module=import_path(path)

    def _get_module(self):
        if not hasattr(self,'_module'):
            self.verify_module(self.path)
            self._module = import_path(self.path)
        return self._module
    module = property(_get_module)

    @classmethod
    def create(cls,path,**opts):
        """Create an empty migration script"""
        cls.require_notfound(path)

        src=template.default_script()
        shutil.copy(src,path)

    @classmethod
    def verify(cls,path):
        # Verifying valid python script is done when .module is referenced
        super(PythonFile,cls).verify(path)

    @classmethod
    def verify_module(cls,path):
        """Ensure this is a valid script, or raise InvalidScriptError"""
        # Try to import and get the upgrade() func
        try:
            module=import_path(path)
        except:
            # If the script itself has errors, that's not our problem
            raise
        try:
            assert callable(module.upgrade)
        except Exception,e:
            raise InvalidScriptError(path+': %s'%str(e))

    def compile(self,database,operation,path=None):
        """Compile a Python script into a logfile or log object"""
        # Change the engine referenced by all migration scripts
        try:
            run.engine.reset(database)
        except (ImportError,exceptions.InvalidRequestError):
            raise ScriptError("The database %s doesn't exist"%database)
        # Run the migration function. Must exist if script/op are valid
        try:
            funcname = operations[operation]
        except KeyError:
            raise ScriptError("%s is not a valid migration function"%operation)
        try:
            func = getattr(self.module,funcname)
        except AttributeError:
            raise ScriptError("The function %s is not defined in this script"%operation)
        func()
        # Success - return the log, or a file containing the log if path given
        ret = run.engine.logsql
        if path is not None:
            ret = LogsqlFile.create(ret,path)
        return ret
    
