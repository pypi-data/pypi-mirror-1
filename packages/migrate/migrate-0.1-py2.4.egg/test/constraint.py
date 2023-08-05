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
        self.table = Table('mytable',meta,
            Column('id',Integer),
            Column('key',String),
        )
        if self.engine.has_table(self.table.name):
            self.table.drop()
        self.table.create()
        self.assertEquals(self.table.primary_key,[])
    def _define_pk(self,*cols):
        # Add a pk by creating a PK constraint
        pk = PrimaryKeyConstraint(*cols)
        self.assertEquals(pk.c,pk.columns)
        self.assertEquals(list(pk.columns),list(cols))
        pk.create()
        self.table = self.refresh_table()
        self.assertEquals(list(self.table.primary_key),list(cols))

        # Drop the PK constraint
        pk.drop()
        self.table = self.refresh_table()
        self.assertEquals(list(self.table.primary_key),list())
        return pk

    @fixture.supported('postgres')
    def test_define_fk(self):
        """FK constraints can be defined, created, and dropped"""
        # FK target must be unique
        pk = PrimaryKeyConstraint(self.table.c.id)
        pk.create()
        # Add a FK by creating a FK constraint
        fk = ForeignKeyConstraint(self.table.c.key,references=[self.table.c.id])
        self.assertEquals(fk.c, fk.columns)
        self.assertEquals(list(fk.columns), [self.table.c.key])
        self.assertEquals(list(fk.references), [self.table.c.id])
        self.assert_(self.table.c.key.foreign_key is None)

        fk.create()
        self.table = self.refresh_table()
        self.assert_(self.table.c.key.foreign_key is not None)
        self.assert_(self.table.c.key.foreign_key is not None)

        fk.drop()
        self.table = self.refresh_table()
        self.assert_(self.table.c.key.foreign_key is None)

    @fixture.supported('postgres')
    def test_define_pk(self):
        """PK constraints can be defined, created, and dropped"""
        self._define_pk(self.table.c.id)

    @fixture.supported('postgres')
    def test_define_pk_multi(self):
        """Multicolumn PK constraints can be defined, created, and dropped"""
        self._define_pk(self.table.c.id,self.table.c.key)

class IntrospectConstraintTest(fixture.DB):
    level=fixture.DB.CONNECT
    def setUp(self):
        fixture.DB.setUp(self)
        meta = BoundMetaData(self.engine)
        self.table = Table('mytable',meta,
            Column('id',Integer,primary_key=True),
            Column('key',String,ForeignKey('mytable.id')),
        )
        self.table.create()
    def tearDown(self):
        if hasattr(self,'table') and self.engine.has_table(self.table.name):
            self.table.drop()
        fixture.DB.tearDown(self)

    @fixture.supported('postgres')
    def test_introspect_pk(self):
        """Constraints can be introspected from the database"""
        self.assertEquals(list(self.table.primary_key),[self.table.c.id])

        # Introspect PK, given a table object
        constraint = PrimaryKeyConstraint(table=self.table,autoload=True)
        self.assertEquals(list(constraint.columns),list(self.table.primary_key))
        self.assert_(constraint.name is not None)

        # Introspect, given a table name
        constraint = PrimaryKeyConstraint(table=self.table.name,
            autoload=True,engine=self.engine)
        self.assertEquals(list(constraint.columns),list(self.table.primary_key))
        self.assert_(constraint.name is not None)

    @fixture.supported('postgres')
    def test_introspect_fk(self):
        """FK constraints can be introspected from the database"""
        self.assert_(self.table.c.id.foreign_key is None)
        self.assert_(self.table.c.key.foreign_key is not None)

        # Introspect FK, given a column object
        constraint = ForeignKeyConstraint(self.table.c.key,autoload=True)
        self.assertEquals(list(constraint.columns),[self.table.c.key])
        self.assertEquals(list(constraint.references),[self.table.c.id])
        self.assert_(constraint.name is not None)

        # Introspect FK, given a column name
        constraint = ForeignKeyConstraint('key',table=self.table.name,
            autoload=True,engine=self.engine)
        self.assertEquals(list(constraint.columns),[self.table.c.key])
        self.assertEquals(list(constraint.references),[self.table.c.id])
        self.assert_(constraint.name is not None)

class AutonameTest(fixture.DB):
    level=fixture.DB.CONNECT

    def setUp(self):
        fixture.DB.setUp(self)
        meta = BoundMetaData(self.engine)
        self.table = Table('mytable',meta,
            Column('id',Integer),
            Column('key',String),
        )
        if self.engine.has_table(self.table.name):
            self.table.drop()
        self.table.create()
    def tearDown(self):
        if hasattr(self,'table') and self.engine.has_table(self.table.name):
            self.table.drop()
        fixture.DB.tearDown(self)
        
    @fixture.supported('postgres')
    def test_autoname(self):
        """Constraints can guess their name"""
        # Don't supply a name; it should create one
        cons = constraint.PrimaryKeyConstraint(self.table.c.id)
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
