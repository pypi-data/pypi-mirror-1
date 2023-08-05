from migrate.versioning.pathed import *
import script


class InvalidVersionError(Exception):
    pass


class VerNum(object):
    """A version number"""
    _instances=dict()
    def __new__(cls,value):
        val=str(value)
        if val not in cls._instances:
            cls._instances[val] = super(VerNum,cls).__new__(cls,value)
        ret = cls._instances[val]
        return ret
    def __init__(self,value):
        self.value=str(int(value))
        if self < 0:
            raise ValueError("Version number cannot be negative")
    def __repr__(self):
        return str(self.value)
    def __str__(self):
        return str(self.value)
    def __int__(self):
        return int(self.value)
    def __add__(self,value):
        ret=int(self)+int(value)
        return VerNum(ret)
    def __sub__(self,value):
        return self+(int(value)*-1)
    def __cmp__(self,value):
        return int(self)-int(value)


class Collection(Pathed):
    """A collection of versioning scripts in a repository"""
    def __init__(self,path):
        super(Collection,self).__init__(path)
        self.versions=dict()

        ver=self.latest=VerNum(1)
        vers=os.listdir(path)
        # This runs up to the latest *complete* version; stops when one's missing
        while str(ver) in vers:
            verpath=self.version_path(ver)
            self.versions[ver]=Version(verpath)
            ver+=1
        self.latest=ver-1
    
    def version_path(self,ver):
        return os.path.join(self.path,str(ver))
    
    def version(self,vernum=None):
        if vernum is None:
            vernum = self.latest
        return self.versions[VerNum(vernum)]

    def commit(self,path,ver=None,*p,**k):
        """Commit a script to this collection of scripts
        This compiles the script into a group of logsql files
        If there's an error compiling the script, the commit is cancelled
        """
        maxver = self.latest+1
        if ver is None:
            ver = maxver
        # Ver must be valid: can't upgrade past the next version
        # No change scripts exist for 0 (even though it's a valid version)
        if ver > maxver or ver == 0:
            raise InvalidVersionError()
        verpath = self.version_path(ver)
        tmpname = None
        try:
            # If replacing an old version, move it for a moment
            if os.path.exists(verpath):
                tmpname = os.path.join(os.path.split(verpath)[0],"%s_tmp"%ver)
                os.rename(verpath,tmpname)
            # Create version folder; add this Python script to the version
            self.versions[ver] = version = Version.create(verpath)
            script = version.commit(path,*p,**k)
        except:
            # Can't leave the folder created above...
            shutil.rmtree(verpath)
            # Move old file back
            if tmpname is not None:
                os.rename(tmpname,verpath)
            raise
        # Success: mark latest; delete old version
        if tmpname is not None:
            shutil.rmtree(tmpname)
        self.latest = ver
    
    @classmethod
    def clear(cls):
        Pathed.clear(cls)
        Version.clear()
    

class extensions:
    """A namespace for file extensions"""
    py='py'
    logsql='logsql'


class Version(Pathed):
    """A single version in a repository
    File must be a directory with an integer name.
    logsql files are named with the version, DBMS, and operation (up or down).

    ex. 
    1/
        1.py
        1.postgres.up.logsql
        1.postgres.down.logsql
        1.sqlite.up.logsql
        1.sqlite.down.logsql
        ...
    """
    def __init__(self,path):
        super(Version,self).__init__(path)
        # Version must be numeric
        try:
            self.version=VerNum(os.path.basename(path))
        except:
            raise InvalidVersionError(path)
        # Collect scripts in this folder
        try:
            self.python = self.logsql = None 
            for script in os.listdir(path):
                self._add_script(os.path.join(path,script))
        except:
            raise
            raise InvalidVersionError(path)
    
    def script(self,database=None,operation=None):
        if database is None and operation is None:
            return self._script_py()
        return self._script_logsql(database,operation)
    def _script_py(self):
        return self.python
    def _script_logsql(self,database,operation):
        return self.logsql[database][operation]

    @classmethod
    def create(cls,path):
        os.mkdir(path)
        try:
            ret=cls(path)
        except:
            os.rmdir(path)
            raise
        return ret

    def _add_script(self,path):
        if path.endswith(extensions.py):
            self._add_script_py(path)
        elif path.endswith(extensions.logsql):
            self._add_script_logsql(path)
    def _add_script_logsql(self,path):
        try:
            version,dbms,op,ext=path.split('.',3)
        except:
            raise script.ScriptError("Invalid logsql script name %s"%path)

        # File the script into a dictionary
        if self.logsql is None:
            self.logsql = dict()
        dbmses = self.logsql
        if dbms not in dbmses:
            dbmses[dbms] = dict()
        ops = dbmses[dbms]
        ops[op] = script.LogsqlFile(path)
    def _add_script_py(self,path):
        self.python = script.PythonFile(path)

    def _rm_ignore(self,path):
        """Try to remove a path; ignore failure"""
        try:
            os.remove(path)
        except OSError:
            pass

    def _compile_one(self,sourcefile,db,op,path,required=None):
        """Given a valid python fileobject, create a single logsql file
        On failure, return None; success, return the path of the new file
        """
        if required is None:
            required = ()
        try:
            try:
                logsql = sourcefile.compile(db,op,path)
                self._add_script(logsql.path)
            except:
                # Always remove the bad file; but we might do more processing
                self._rm_ignore(path)
                raise
        except (script.ScriptError,NotImplementedError):
            # Some compile failures are ok: we don't need all DBs
            if db in required:
                raise
    def _compile(self,path_py,required=None):
        """Given a valid Python file, create all possible logsql files"""
        # This must be done before moving the Python file: dependencies, errors
        sourcefile = script.PythonFile(path_py)
        path_tmpl = os.path.join(self.path,'%s.%%s.%%s.%s'
            %(self.version,extensions.logsql))
        paths = []  # all paths compiled so far
        try:
            for db in databases:
                for op in operations.keys():
                    path = path_tmpl%(db,op)
                    paths.append(path)
                    self._compile_one(sourcefile,db,op,path,required=required)
        except:
            # Delete all other created files on failure
            for path in paths:
                self._rm_ignore(path)
            raise
    def commit(self,path_py,required=None):
        # Assume this is a Python script for now (later: allow .sql)
        dest = os.path.join(self.path,'%s.%s'%(str(self.version),extensions.py))
        if (not os.path.exists(path_py)) or (not os.path.isfile(path_py)):
            raise InvalidVersionError(path)

        # Create logsql files
        self._compile(path_py,required=required)

        # Success. Move the committed py script to this version's folder.
        os.rename(path_py,dest)
        self._add_script(dest)
        # Also delete the .pyc file, if it exists
        path_pyc = path_py+'c'
        if os.path.exists(path_pyc):
            self._rm_ignore(path_pyc)
