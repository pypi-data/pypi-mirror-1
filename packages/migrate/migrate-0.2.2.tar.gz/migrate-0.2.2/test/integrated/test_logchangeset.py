from test import fixture
from sqlalchemy import *
from migrate.versioning import logengine
from migrate.changeset import *

class TestLogChangeset(fixture.DB):
    level = fixture.DB.CONNECT

    def setUp(self):
        fixture.DB.setUp(self)
        self.logengine = create_engine(self.url,strategy='logsql')
        self.meta = DynamicMetaData()
        self.meta.connect(self.logengine)
        self.table = None
    def tearDown(self):
        if self.table and self.engine.has_table(self.table.name):
            self.meta.connect(self.engine)
            self.table.drop()
        fixture.DB.tearDown(self)

    @fixture.usedb(supported='postgres')
    def test_logchangeset(self):
        """Logengine: Create/drop various changeset items"""
        self.table = Table('tmp',self.meta,
            Column('id',Integer),
        )
        # We're not validating any of what's below; that's done in other unit
        # tests. This just ensures LogEngine can run them without error. 
        self.table.create()
        self.table.create_column(Column('key',String,nullable=True))
        pk = PrimaryKeyConstraint(self.table.c.id)
        pk.create()
        fk = ForeignKeyConstraint([self.table.c.key],[self.table.c.id])
        fk.create()
        self.table.c.key.alter(nullable=False)
        fk.drop()
        pk.drop()
        self.table.drop_column(self.table.c.key)
        self.table.rename('pmt')
        self.table.rename('tmp')
        index = Index('indexname',self.table.c.id)
        index.create()
        index.rename('emanxedni')
        index.drop()

        # This should not error
        log = self.logengine.logsql
        log.run(self.engine)

        # It should've actually run
        self.assert_(self.engine.has_table(self.table.name))
