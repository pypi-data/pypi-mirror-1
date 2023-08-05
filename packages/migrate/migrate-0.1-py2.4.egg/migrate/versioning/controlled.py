from sqlalchemy import *
from base import *
from migrate.versioning.repository import Repository
from migrate.versioning.version import VerNum

class ControlledSchema(object):
    """A database under version control"""
    class Error(Exception):
        pass
    class InvalidVersionError(Error):
        """Invalid version number"""
    class DatabaseNotControlledError(Error):
        """Database shouldn't be under vc, but it is"""
    class DatabaseAlreadyControlledError(Error):
        """Database should be under vc, but it's not"""
    class WrongRepositoryError(Error):
        """This database is under version control by another repository"""
    
    #def __init__(self,connection,repository=None):
    def __init__(self,connection,repository):
        if type(repository) is str:
            repository=Repository(repository)
        self.connection = connection
        self.repository = repository
        self.meta=BoundMetaData(connection.engine)
        #if self.repository is None:
        #   self._get_repository()
        self._load()
    
    def __eq__(self,other):
        return (self.repository is other.repository \
            and self.version == other.version)
    
    def _load(self):
        """Load controlled schema version info from DB"""
        tname = self.repository.version_table
        self.meta=BoundMetaData(self.connection.engine)
        if not hasattr(self,'table') or self.table is None:
            try:
                self.table=Table(tname,self.meta,autoload=True)
            except (exceptions.NoSuchTableError):
                raise self.DatabaseNotControlledError(tname)
        # TODO?: verify that the table is correct (# cols, etc.)
        result = self.connection.execute(self.table.select(),)
        data = list(result)[0]
        # TODO?: exception if row count is bad
        # TODO: check repository id, exception if incorrect
        self.version = data['version']
    
    def _get_repository(self):
        """Given a database connection, try to guess the repository"""
        # TODO: no guessing yet; for now, a repository must be supplied
        raise NotImplementedError
    
    @classmethod
    def create(cls,connection,repository,version=None):
        """Declare a database to be under a repository's version control"""
        # Confirm that the version # is valid: positive, integer, exists in repos
        if type(repository) is str:
            repository=Repository(repository)
        version = cls._validate_version(repository,version)
        table=cls._create_table_version(connection,repository,version)
        # TODO: history table
        # Load repository information and return
        return cls(connection,repository)
    
    @classmethod
    def _validate_version(cls,repository,version):
        """Ensures this is a valid version number for this repository
        If invalid, raises cls.InvalidVersionError
        Returns a valid version number
        """
        if version is None:
            version=0
        try:
            version = VerNum(version) # raises valueerror
            if version < 0 or version > repository.latest:
                raise ValueError
        except ValueError:
            raise cls.InvalidVersionError(version)
        return version
    
    @classmethod
    def _create_table_version(cls,connection,repository,version):
        """Creates the versioning table in a database"""
        # Create tables
        tname = repository.version_table
        meta=BoundMetaData(connection.engine)
        try:
            table=Table(tname,meta,
                #Column('repository_id',String,primary_key=True), # MySQL needs a length
                Column('repository_id',String(255),primary_key=True),
                Column('repository_path',String),
                Column('version',Integer),
            )
            table.create(connection)
        except (exceptions.ArgumentError,exceptions.SQLError):
            # The table already exists
            raise cls.DatabaseAlreadyControlledError()
        # Insert data
        connection.execute(table.insert(),repository_id=repository.id,
            repository_path=repository.path,version=int(version))
        return table

    def drop(self):
        """Remove version control from a database"""
        try:
            self.table.drop(self.connection)
        except (exceptions.SQLError):
            raise self.DatabaseNotControlledError(str(self.table))
    
    def _engine_db(self,engine):
        """Returns the database name of an engine - 'postgres','sqlite'..."""
        # TODO: This is a bit of a hack...
        return str(engine.dialect.__module__).split('.')[-1]

    def changeset(self,version=None):
        database = self._engine_db(self.connection.engine)
        start_ver = self.version
        changeset = self.repository.changeset(database,start_ver,version)
        return changeset
    
    def runchange(self,ver,change,step):
        startver = ver
        endver = ver + step
        # Current database version must be correct! Don't run if corrupt!
        if self.version != startver:
            raise self.InvalidVersionError("%s is not %s"%(self.version,startver))
        # Run the change; update database version; refresh
        change.run(self.connection.engine,self.connection)
        self.connection.execute(self.table.update(
            self.table.c.version == int(startver)), version = int(endver))
        self._load()
        
    def upgrade(self,version=None):
        """Upgrade (or downgrade) to a specified version, or latest version"""
        changeset = self.changeset(version)
        for ver,change in changeset:
            self.runchange(ver,change,changeset.step)
