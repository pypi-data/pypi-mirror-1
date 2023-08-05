import fixture
from migrate.versioning.repository import *
from migrate.versioning import exceptions
import os,shutil
from migrate.versioning import logengine

class RepositoryTests(fixture.Pathed):
    def test_create(self):
        """Repositories are created successfully"""
        path=self.tmp_repos()
        name='repository_name'
        # Creating a repository that doesn't exist should succeed
        repos=Repository.create(path,name)
        config_path=repos.config.path
        manage_path=os.path.join(repos.path,'manage.py')
        self.assert_(repos)
        # Files should actually be created
        self.assert_(os.path.exists(path))
        self.assert_(os.path.exists(config_path))
        self.assert_(os.path.exists(manage_path))
        # Can't create it again: it already exists
        self.assertRaises(exceptions.PathFoundError,Repository.create,path,name)
        return path
    
    def test_load(self):
        """We should be able to load information about an existing repository"""
        # Create a repository to load
        path=self.test_create()
        repos=Repository(path)
        self.assert_(repos)
        self.assert_(repos.config)
        self.assert_(repos.config.get('db_settings','version_table'))
        # version_table's default isn't none
        self.assertNotEquals(repos.config.get('db_settings','version_table'),'None')
    
    def test_load_notfound(self):
        """Nonexistant repositories shouldn't be loaded"""
        path=self.tmp_repos()
        self.assert_(not os.path.exists(path))
        self.assertRaises(exceptions.InvalidRepositoryError,Repository,path)

    def test_load_invalid(self):
        """Invalid repos shouldn't be loaded"""
        # Here, invalid=empty directory. There may be other conditions too, 
        # but we shouldn't need to test all of them
        path=self.tmp_repos()
        os.mkdir(path)
        self.assertRaises(exceptions.InvalidRepositoryError,Repository,path)


class VersionedRepository(fixture.Pathed):
    """Tests on an existing repository with a single python script"""
    def setUp(self):
        Repository.clear()
        self.path_repos=self.tmp_repos()
        self.path_script=self.tmp_py()
        # Create repository, script
        Repository.create(self.path_repos,'repository_name')

    def test_commit(self):
        """Commit scripts to a repository and detect repository version"""
        # Load repository; commit script by pathname; script should go away
        script.PythonFile.create(self.path_script)
        repos=Repository(self.path_repos)
        self.assert_(os.path.exists(self.path_script))
        repos.commit(self.path_script)
        self.assert_(not os.path.exists(self.path_script))
        # .pyc file from the committed script shouldn't exist either
        self.assert_(not os.path.exists(self.path_script+'c'))
    def test_version(self):
        """We should correctly detect the version of a repository"""
        script.PythonFile.create(self.path_script)
        repos=Repository(self.path_repos)
        # Get latest version, or detect if a specified version exists
        self.assertEquals(repos.latest,0)
        # repos.latest isn't an integer, but a VerNum
        # (so we can't just assume the following tests are correct)
        self.assert_(repos.latest>=0)
        self.assert_(repos.latest<1)
        # Commit a script and test again
        repos.commit(self.path_script)
        self.assertEquals(repos.latest,1)
        self.assert_(repos.latest>=0)
        self.assert_(repos.latest>=1)
        self.assert_(repos.latest<2)
        # Commit a new script and test again
        script.PythonFile.create(self.path_script)
        repos.commit(self.path_script)
        self.assertEquals(repos.latest,2)
        self.assert_(repos.latest>=0)
        self.assert_(repos.latest>=1)
        self.assert_(repos.latest>=2)
        self.assert_(repos.latest<3)
    def test_source(self):
        """Get a script object by version number and view its source"""
        script.PythonFile.create(self.path_script)
        # Load repository and commit script
        repos=Repository(self.path_repos)
        repos.commit(self.path_script)
        # Get script object
        source=repos.version(1).script().source()
        # Source is valid: script must have an upgrade function
        # (not a very thorough test, but should be plenty)
        self.assert_(source.find('def upgrade')>=0)
    def test_latestversion(self):
        script.PythonFile.create(self.path_script)
        """Repository.version() (no params) returns the latest version"""
        repos=Repository(self.path_repos)
        repos.commit(self.path_script)
        self.assert_(repos.version(repos.latest) is repos.version())
        self.assert_(repos.version() is not None)
    def test_sqllog(self):
        """Committing a script should create the right files (ex. sql logs)"""
        # Load repository and commit script
        repos=Repository(self.path_repos)
        script.PythonFile.create(self.path_script,logsql=True)
        repos.commit(self.path_script)
        version = repos.version()
        # Confirm the correct files exist where they should
        paths=[]
        def exists(path,container=None):
            """Ensure the existence and uniqueness of paths
            Optionally, ensure a path is contained in some other path
            """
            if container is not None:
                self.assert_(path.startswith(container),"%s does not contain %s"
                    %(path,container))
            self.assert_(path not in paths,"path %s is not unique (%r)"%(path,paths))
            
            self.assert_(os.path.exists(path),"path %s does not exist")
            paths.append(path)
        exists(repos.path)
        exists(version.path,repos.path)
        exists(version.script().path,version.path)
        #for dbname in databases:
        for dbname in ('postgres','sqlite'):
            for opname in operations.keys():
                exists(version.script(dbname,opname).path,version.path)
        # Confirm that the above didn't pass trivially..
        #self.assert_('postgres' in databases)
        #self.assert_('mysql' in databases)
        #self.assert_('sqlite' in databases)
        self.assert_('upgrade' in operations)
        self.assert_('downgrade' in operations)
    def test_commit_fail(self):
        """Failed commits shouldn't corrupt the repository"""
        repos=Repository(self.path_repos)
        path_script=self.tmp_py()
        text_script = """
        from sqlalchemy import *
        from migrate import *
        logsql = True
        
        def upgrade():
            raise Exception()
        
        def downgrade():
            raise Exception()
        """.replace("\n       ","\n")
        fd=open(path_script,'w')
        fd.write(text_script)
        fd.close()

        # Record current state, and commit
        ver_pre = os.listdir(repos.versions.path)
        repos_pre = os.listdir(repos.path)
        self.assertRaises(Exception,repos.commit,path_script)
        # Version is unchanged
        self.assertEquals(repos.latest,0)
        # No new files created; committed script not moved
        self.assert_(os.path.exists(path_script))
        self.assertEquals(os.listdir(repos.versions.path),ver_pre)
        self.assertEquals(os.listdir(repos.path),repos_pre)
    
    def test_changeset(self):
        """Repositories can create changesets properly"""
        # Create a nonzero-version repository of empty scripts
        repos=Repository(self.path_repos)
        for i in range(10):
            script.PythonFile.create(self.path_script)
            repos.commit(self.path_script)

        def check_changeset(params,length):
            """Creates and verifies a changeset"""
            changeset = repos.changeset('postgres',*params)
            self.assertEquals(len(changeset),length)
            self.assert_(isinstance(changeset,Changeset))
            uniq = list()
            # Changesets are iterable
            for version,change in changeset:
                #self.assert_(isinstance(change,logengine.SqlLog))
                self.assert_(isinstance(change,script.ScriptFile))
                # Changes aren't identical
                self.assert_(id(change) not in uniq)
                uniq.append(id(change))
            return changeset

        # Upgrade to a specified version...
        cs=check_changeset((0,10),10)
        self.assertEquals(cs.keys().pop(0),0) # 0 -> 1: index is starting version
        self.assertEquals(cs.keys().pop(),9) # 9 -> 10: index is starting version
        self.assertEquals(cs.start,0) # starting version
        self.assertEquals(cs.end,10) # ending version
        check_changeset((0,1),1)
        check_changeset((0,5),5)
        check_changeset((0,0),0)
        check_changeset((5,5),0)
        check_changeset((10,10),0)
        check_changeset((5,10),5)
        # Can't request a changeset of higher version than this repository
        self.assertRaises(Exception,repos.changeset,'postgres',5,11)
        self.assertRaises(Exception,repos.changeset,'postgres',-1,5)

        # Upgrade to the latest version...
        cs=check_changeset((0,),10)
        self.assertEquals(cs.keys().pop(0),0)
        self.assertEquals(cs.keys().pop(),9)
        self.assertEquals(cs.start,0)
        self.assertEquals(cs.end,10)
        check_changeset((1,),9)
        check_changeset((5,),5)
        check_changeset((9,),1)
        check_changeset((10,),0)
        # Can't request a changeset of higher/lower version than this repository
        self.assertRaises(Exception,repos.changeset,'postgres',11)
        self.assertRaises(Exception,repos.changeset,'postgres',-1)

        # Downgrade
        cs=check_changeset((10,0),10)
        self.assertEquals(cs.keys().pop(0),10) # 10 -> 9
        self.assertEquals(cs.keys().pop(),1)    # 1 -> 0
        self.assertEquals(cs.start,10)
        self.assertEquals(cs.end,0)
        check_changeset((10,5),5)
        check_changeset((5,0),5)
    

if __name__=='__main__':
    fixture.main()
