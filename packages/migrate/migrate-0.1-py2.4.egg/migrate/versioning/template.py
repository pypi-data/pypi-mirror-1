from pkg_resources import resource_filename
import os,shutil
import sys
from migrate.versioning.base import *
from migrate.versioning import pathed

class Packaged(pathed.Pathed):
    """An object assoc'ed with a Python package"""
    def __init__(self,pkg):
        self.pkg = pkg
        path = self._find_path(pkg)
        super(Packaged,self).__init__(path)

    @classmethod
    def _find_path(cls,pkg):
        pkg_name, resource_name = pkg.rsplit('.',1)
        ret = resource_filename(pkg_name,resource_name)
        return ret

class Collection(Packaged):
    """A collection of templates of a specific type"""
    _default=None
    def _get_default(self):
        return os.path.join(self.path,self._default)
    default = property(_get_default)

    def _get_default_pkg(self):
        return (self.pkg,self._default)
    default_pkg = property(_get_default_pkg)

class RepositoryCollection(Collection):
    _default='default'

class ScriptCollection(Collection):
    _default='default.py'

class Template(Packaged):
    """Finds the paths/packages of various Migrate templates"""
    _repository='repository'
    _script='script'

    def __init__(self,pkg):
        super(Template,self).__init__(pkg)
        self.repository=RepositoryCollection('.'.join((self.pkg,self._repository)))
        self.script=ScriptCollection('.'.join((self.pkg,self._script)))

    def _default_item(self,attr,as_pkg=None,as_str=None):
        item = getattr(self,attr)
        if not as_pkg:
            return str(item.default)
        ret = item.default_pkg
        if as_str:
            ret = '.'.join(ret)
        return ret

    def default_repository(self,as_pkg=None,as_str=None):
        return self._default_item('repository',as_pkg,as_str)
    
    def default_script(self,as_pkg=None,as_str=None):
        return self._default_item('script',as_pkg,as_str)

template_pkg='migrate.versioning.templates'
template=Template(template_pkg)
