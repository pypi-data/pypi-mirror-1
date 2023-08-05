import fixture
import sys
import os
from sqlalchemy import *
from StringIO import StringIO
from migrate.versioning.base import *
from migrate.versioning import logengine,script

class LogEngineTest(fixture.DB):
    # We need to create our own connection
    level=fixture.DB.NONE
    def spliturl(self,url):
        return url.split('://',1)[0]
    def setUp(self):
        super(LogEngineTest,self).setUp()
        self.exec_engine = create_engine(self.url)
        self.exec_conn=self.exec_engine.connect()
    def tearDown(self):
        super(LogEngineTest,self).tearDown()
        self.stream.close()
        self.exec_conn.close()

    def _test(self):
        """LogEngine can log and run some simple SQL correctly"""
        self.stream=StringIO()
        self.assertEquals(self.log_engine.logsql,"")
        tablename='tmptable'
        self.ignoreErrors(self.exec_conn.execute,"drop table %s"%tablename)
        # Run some SQL; logged
        meta=BoundMetaData(self.log_engine)
        table=Table(tablename,meta,
            Column('id',Integer,primary_key=True),
        )
        table.create()
        self.log_conn.execute(table.insert(),id=42)
        self.log_conn.execute(table.update(table.c.id==42),id=11)
        self.log_conn.execute(text("update %s set id=13 where id=11"%tablename))

        # Above isn't actually executed: table doesn't exist yet
        query="select * from %s"%tablename
        self.assertRaises(exceptions.SQLError,self.exec_conn.execute,query)

        # Write output to a log; reload it
        self.log_engine.write(self.stream)
        self.stream.seek(0)
        log=logengine.load(self.stream)

        # Loaded log should be identical to saved log, but not a reference
        self.assertEquals(self.log_engine.logsql,log)
        self.assertEquals(str(self.log_engine.logsql),str(log))
        self.assert_(self.log_engine.logsql is not log)
        self.assert_(hasattr(self.log_engine,'drivername'))

        # Run the log
        log.run(self.exec_engine,self.exec_conn)
        # Confirm correctness
        results = list(self.exec_conn.execute(query))
        self.assertEquals(len(results),1)
        self.assertEquals(results[0]['id'],13)
        self.exec_conn.execute("drop table %s"%tablename)
        
        return log

class LogEngineSql(LogEngineTest):
    def setUp(self):
        super(LogEngineSql,self).setUp()
        self.log_engine = create_engine(self.url,strategy='logsql')
        self.log_conn=self.log_engine.connect()
    def tearDown(self):
        super(LogEngineSql,self).tearDown()
        self.log_conn.close()
    
    def test_sql(self):
        return self._test()
    
class LogEngineUrl(LogEngineTest,fixture.Pathed):
    def setUp(self):
        super(LogEngineUrl,self).setUp()
    def tearDown(self):
        super(LogEngineUrl,self).tearDown()
        self.log_conn.close()
    def test_url(self):
        """LogEngine can be initialized properly with only the database as a url"""
        # Get the engine type out of the url
        dbms = self.spliturl(self.url)
        # 'dbms' is something like 'sqlite','postgres','mysql',etc.
        self.log_engine = create_engine(dbms,strategy='logsql')
        self.log_conn = self.log_engine.connect()

        # Our tests should pass with this engine, too
        self._test()
    def test_change(self):
        """LogEngine can change the dbms it's using"""
        dbms1 = 'sqlite'
        dbms2 = self.spliturl(self.url)

        self.log_engine = create_engine(dbms1,strategy='logsql')
        self.assertEquals(self.log_engine.drivername,dbms1)
        self.log_conn = self.log_engine.connect()
        # Create a db to run this log against; move the old exec_* for a moment
        exec_engine_tmp = self.exec_engine
        exec_conn_tmp = self.exec_conn
        self.exec_engine = create_engine('sqlite:///'+self.tmp())
        self.exec_conn=self.exec_engine.connect()
        log1=self._test()
        self.exec_conn.close()
        self.exec_engine = exec_engine_tmp
        self.exec_conn = exec_conn_tmp
        self.log_conn.close()

        self.log_engine.reset(dbms2)
        self.assertEquals(self.log_engine.drivername,dbms2)
        self.log_conn = self.log_engine.connect()
        log2=self._test()

        # If the DBs being used are different, their output should be too
        if dbms1 != dbms2:
            self.assertNotEquals(log1,log2)

    def test_emptyurl(self):
        """Can create LogEngine with no URL and change it"""
        self.log_engine = create_engine(None,strategy='logsql')

        self.log_engine.reset(self.spliturl(self.url))
        self.log_conn = self.log_engine.connect()
        self._test()

script_text="""
from sqlalchemy import *
from migrate import *

#conn=migrate_engine.connect()
meta=BoundMetaData(migrate_engine)
table = Table('tmp',meta,
    Column('id',Integer,primary_key=True),
)
def upgrade():
    table.create()
    #conn.execute(table.insert(),id=42)
    #conn.execute(table.update(table.c.id==42),id=11)
    #conn.execute(text("update %s set id=13 where id=11"%table.name))
    table.insert().execute(id=42)
    table.update(table.c.id==42).execute(id=11)
    text("update %s set id=13 where id=11"%table.name,\
        engine=migrate_engine).execute()
    

def downgrade():
    table.drop()
"""

class LogEngineScript(LogEngineTest,fixture.Pathed):
    def setUp(self):
        LogEngineTest.setUp(self)
        fixture.Pathed.setUp(self)
        self.stream=StringIO()
    def tearDown(self):
        LogEngineTest.tearDown(self)
        fixture.Pathed.tearDown(self)
    def xtest_run(self):
        """Can correctly create/load/run logsql objects from a given py script"""
        # Write and load the script
        script_path=self.tmp_py()
        fd=open(script_path,'w')
        fd.write(script_text)
        fd.close()
        py = script.PythonFile(script_path)
        self.log_engine = create_engine(self.url,strategy='logsql')

        # Create logsql objects, run them on database
        def run_op(opname):
            op = operations[opname]
            log = py.compile(self.log_engine.drivername,op)
            self.assert_(isinstance(log,logengine.SqlLog))
            self.assertNotEquals(str(log),'')
            log.run(self.exec_engine,self.exec_conn)

        query='select * from tmp'
        self.ignoreErrors(run_op,'downgrade')
        self.assertRaises(Exception,self.exec_conn.execute,query)
        run_op('upgrade')
        self.exec_conn.execute(query) # no exception: table exists
        run_op('downgrade')
        self.assertRaises(Exception,self.exec_conn.execute,query)

        # Create logsql files, run them on database
        def run_op(op,path):
            log = py.compile(self.log_engine.drivername,op)
            file = py.compile(self.log_engine.drivername,op,path)
            self.assert_(isinstance(file,script.LogsqlFile))
            self.assertEquals(log,file.log)
            self.assert_(os.path.exists(file.path))
            file.run(self.exec_engine,self.exec_conn)

        self.assertRaises(Exception,self.exec_conn.execute,query)
        run_op('upgrade',self.tmp())
        self.exec_conn.execute(query) # no exception: table exists
        run_op('downgrade',self.tmp())
        self.assertRaises(Exception,self.exec_conn.execute,query)

if __name__=='__main__':
    fixture.main()
