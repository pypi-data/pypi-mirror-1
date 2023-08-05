from base import Base
from pathed import Pathed
from sqlalchemy import create_engine,create_session,Table
from pkg_resources import resource_stream

def readurls():
    filename='test_db.cfg'
    ret=[]
    tmpfile=Pathed.tmp()
    #fd=open(filename)
    fd = resource_stream('__main__',filename)
    for line in fd:
        if line.startswith('#'):
            continue
        line=line.replace('__tmp__',tmpfile).strip()
        ret.append(line)
    fd.close()
    return ret

def supported(*databases):
    """Defines the databases a particular test supports
    All not listed are not supported (tests aren't run)
    Opposite of not_supported()
    """
    def entangle(func):
        setattr(func,'supported',databases)
        return func
    return entangle

def not_supported(*databases):
    """Defines the databases a particular test does not support
    All not listed are supported (test will run)
    Opposite of supported()
    """
    def entangle(func):
        setattr(func,'not_supported',databases)
        return func
    return entangle

class DB(Base):
    # Constants: connection level
    NONE=0  # No connection; just set self.url
    CONNECT=1   # Connect; no transaction
    TXN=2   # Everything in a transaction

    level=TXN
    urls=readurls()
    # url: engine
    engines=dict([(url,create_engine(url)) for url in urls])

    def shortDescription(self,*p,**k):
        """List database connection info with description of the test"""
        ret = super(DB,self).shortDescription(*p,**k) or str(self)
        engine = self._engineInfo()
        if engine is not None:
            ret = "(%s) %s"%(engine,ret)
        return ret

    def _engineInfo(self,url=None):
        if url is None: 
            url=self.url
        return url

    def _connect(self,url):
        self.url = url
        self.engine = self.engines[url]
        if self.level < self.CONNECT: 
            return
        self.conn = self.engine.connect()
        self.session = create_session(bind_to=self.conn)
        if self.level < self.TXN: 
            return
        self.txn = self.session.create_transaction()
        self.txn.add(self.conn)

    def _disconnect(self):
        if hasattr(self,'txn'):
            self.txn.rollback()
        if hasattr(self,'session'):
            self.session.close()
        if hasattr(self,'conn'):
            self.conn.close()

    def run(self,*p,**k):
        """Run one test for each connection string"""
        for url in self.urls:
            self._run_one(url,*p,**k)

    def _supported(self,url):
        db = url.split(':',1)[0]
        func = getattr(self,self._TestCase__testMethodName)
        if hasattr(func,'supported'):
            return db in func.supported
        if hasattr(func,'not_supported'):
            return not (db in func.not_supported)
        # Neither list assigned; assume all are supported
        return True
    def _not_supported(self,url):
        return not self._supported(url)
    
    def _run_one(self,url,*p,**k):
        if self._not_supported(url):
            return
        self._connect(url)
        try:
            super(DB,self).run(*p,**k)
        finally:
            self._disconnect()

    def refresh_table(self,table=None,newname=None):
        """Reload the table from the database"""
        if table is None:
            table = self.table
        meta = table.metadata
        table.deregister()
        if newname is not None:
            table.name = newname
        ret = Table(table.name,meta,redefine=True,autoload=True)
        return ret
    
