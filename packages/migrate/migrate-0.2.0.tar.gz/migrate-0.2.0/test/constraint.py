from sqlalchemy import *
import fixture
from migrate.changeset import *

class ConstraintTest(fixture.DB):
    level=fixture.DB.CONNECT
    def setUp(self):
        fixture.DB.setUp(self)
        self._create_table()
    def tearDown(self):
        if hasattr(self,'table') and self.engine.has_table(self.table.name):
            self.table.drop()
        fixture.DB.tearDown(self)

    def _create_table(self):
        meta = BoundMetaData(self.engine)
        meta.clear()
        self.table = Table('mytable',meta,
            Column('id',Integer),
            Column('fkey',Integer),
            mysql_engine='InnoDB'
        )
        if self.engine.has_table(self.table.name):
            self.table.drop()
        self.table.create()
        #self.assertEquals(self.table.primary_key,[])
        self.assertEquals(len(self.table.primary_key),0)
        self.assert_(isinstance(self.table.primary_key,
            schema.PrimaryKeyConstraint),self.table.primary_key.__class__)
    def _define_pk(self,*cols):
        # Add a pk by creating a PK constraint
        pk = PrimaryKeyConstraint(*cols)
        self.assertEquals(list(pk.columns),list(cols))
        if self.url.startswith('oracle'):
            # Can't drop Oracle PKs without an explicit name
            pk.name = 'fgsfds'
        pk.create()
        self.table = self.refresh_table()
        self.assertEquals(list(self.table.primary_key),list(cols))
        #self.assert_(self.table.primary_key.name is not None)

        # Drop the PK constraint
        if not self.url.startswith('oracle'):
            # Apparently Oracle PK names aren't introspected
            pk.name = self.table.primary_key.name
        pk.drop()
        self.table = self.refresh_table()
        #self.assertEquals(list(self.table.primary_key),list())
        self.assertEquals(len(self.table.primary_key),0)
        self.assert_(isinstance(self.table.primary_key,
            schema.PrimaryKeyConstraint),self.table.primary_key.__class__)
        return pk

    #@fixture.supported('postgres','mysql')
    @fixture.not_supported('sqlite')
    def test_define_fk(self):
        """FK constraints can be defined, created, and dropped"""
        # FK target must be unique
        pk = PrimaryKeyConstraint(self.table.c.id)
        pk.create()
        # Add a FK by creating a FK constraint
        self.assert_(self.table.c.fkey.foreign_key is None)
        fk = ForeignKeyConstraint([self.table.c.fkey],[self.table.c.id])
        self.assert_(self.table.c.fkey.foreign_key is not None)
        #self.assertEquals(fk.c, fk.columns)
        self.assertEquals(list(fk.columns), [self.table.c.fkey])
        self.assertEquals([e.column for e in fk.elements],[self.table.c.id])
        self.assertEquals(list(fk.referenced),[self.table.c.id])

        if self.url.startswith('mysql'):
            # MySQL FKs need an index
            index = Index('index_name',self.table.c.fkey)
            index.create()
        if self.url.startswith('oracle'):
            # Oracle constraints need a name
            fk.name = 'fgsfds'
        fk.create()
        self.table = self.refresh_table()
        self.assert_(self.table.c.fkey.foreign_key is not None)

        fk.drop()
        self.table = self.refresh_table()
        self.assert_(self.table.c.fkey.foreign_key is None)

    #@fixture.supported('postgres','sqlite','mysql')
    def test_define_pk(self):
        """PK constraints can be defined, created, and dropped"""
        self._define_pk(self.table.c.id)

    #@fixture.supported('postgres','sqlite','mysql')
    def test_define_pk_multi(self):
        """Multicolumn PK constraints can be defined, created, and dropped"""
        self._define_pk(self.table.c.id,self.table.c.fkey)


class AutonameTest(fixture.DB):
    level=fixture.DB.CONNECT

    def setUp(self):
        fixture.DB.setUp(self)
        meta = BoundMetaData(self.engine)
        self.table = Table('mytable',meta,
            Column('id',Integer),
            Column('fkey',String(40)),
        )
        if self.engine.has_table(self.table.name):
            self.table.drop()
        self.table.create()
    def tearDown(self):
        if hasattr(self,'table') and self.engine.has_table(self.table.name):
            self.table.drop()
        fixture.DB.tearDown(self)
        
    #@fixture.supported('postgres','sqlite','mysql')
    @fixture.not_supported('oracle')
    def test_autoname(self):
        """Constraints can guess their name if none is given"""
        # Don't supply a name; it should create one
        cons = PrimaryKeyConstraint(self.table.c.id)
        cons.create()
        self.table = self.refresh_table()
        self.assertEquals(list(cons.columns),list(self.table.primary_key))

        # Remove the name, drop the constraint; it should succeed
        cons.name = None
        cons.drop()
        self.table = self.refresh_table()
        self.assertEquals(list(),list(self.table.primary_key))

if __name__=='__main__':
    fixture.main()
