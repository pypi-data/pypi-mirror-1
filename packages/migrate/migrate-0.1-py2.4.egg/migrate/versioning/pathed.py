from migrate.versioning.base import *
from unique_instance import UniqueInstance
import os,shutil

class PathNotFoundError(Exception):
    """A path with no file was required; found a file"""
    pass

class PathFoundError(Exception):
    """A path with a file was required; found no file"""
    pass

class Pathed(UniqueInstance):
    """A class associated with a path/directory tree"""
    parent=None
    """The parent class of this class; should be another Pathed class or none
    (ie. the class of the containing folder)
    """

    @classmethod
    def _key(cls,path):
        return str(path)

    def __init__(self,path):
        self.path=path
        if self.__class__.parent is not None:
            self._init_parent(path)

    def _init_parent(self,path):
        """Try to initialize this object's parent, if it has one"""
        parent_path=self.__class__._parent_path(path)
        self.parent=self.__class__.parent(parent_path)
        log.info("Getting parent %r:%r"%(self.__class__.parent,parent_path))
        self.parent._init_child(path,self)
    
    def _init_child(self,child,path):
        """Run when a child of this object is initialized
        Parameters: the child object; the path to this object (its parent)
        """
        pass
    
    @classmethod
    def _parent_path(cls,path):
        """Fetch the path of this object's parent from this object's path
        """
        # os.path.dirname(), but strip directories like files (like unix basename)
        # Treat directories like files...
        if path[-1]=='/':
            path=path[:-1]
        ret = os.path.dirname(path)
        return ret

    @classmethod
    def require_notfound(cls,path):
        """Ensures a given path does not already exist"""
        if os.path.exists(path):
            raise PathFoundError(path)
    
    @classmethod
    def require_found(cls,path):
        """Ensures a given path already exists"""
        if not os.path.exists(path):
            raise PathNotFoundError(path)

    def __str__(self):
        return self.path
    
