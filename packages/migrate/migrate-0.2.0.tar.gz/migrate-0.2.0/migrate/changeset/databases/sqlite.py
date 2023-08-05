from migrate.changeset import ansisql,util,constraint
from sqlalchemy.databases import sqlite
import sqlalchemy
from migrate.changeset import exceptions

class SQLiteColumnGenerator(sqlite.SQLiteSchemaGenerator,ansisql.ANSIColumnGenerator):
    pass
class SQLiteColumnDropper(ansisql.ANSIColumnDropper):
    def visit_column(self,column):
        raise exceptions.NotSupportedError("SQLite does not support "
            "DROP COLUMN; see http://www.sqlite.org/lang_altertable.html")
class SQLiteSchemaChanger(ansisql.ANSISchemaChanger):
    def _not_supported(self,op):
        raise exceptions.NotSupportedError("SQLite does not support "
            "%s; see http://www.sqlite.org/lang_altertable.html"%op)
    def _visit_column_nullable(self,table_name,col_name,delta):
        return self._not_supported('ALTER TABLE')
    def _visit_column_default(self,table_name,col_name,delta):
        return self._not_supported('ALTER TABLE')
    def _visit_column_type(self,table_name,col_name,delta):
        return self._not_supported('ALTER TABLE')
    def _visit_column_name(self,table_name,col_name,delta):
        return self._not_supported('ALTER TABLE')
    def visit_index(self,param):
        self._not_supported('ALTER INDEX')
class SQLiteConstraintGenerator(ansisql.ANSIConstraintGenerator):
    pass
class SQLiteConstraintGenerator(ansisql.ANSIConstraintGenerator):
    def visit_constraint(self,item):
        if isinstance(item,constraint.PrimaryKeyConstraint):
            # In SQLite, PK constraints created after the table are the same as
            # unique indexes
            self.append("CREATE UNIQUE INDEX ")
            self.append(item.name or item.autoname())
            self.append(" ON ")
            self.append(item.table.fullname)
            cols = ','.join([c.name for c in item.columns])
            self.append(' (%s)'%cols)
            self.execute()
        elif isinstance(item,constraint.ForeignKeyConstraint):
            pass    # SQLite doesn't use FKs
class SQLiteConstraintDropper(ansisql.ANSIConstraintDropper):
    def visit_constraint(self,item):
        if isinstance(item,constraint.PrimaryKeyConstraint):
            # In SQLite, PK constraints created after the table are the same as
            # unique indexes
            self.append("DROP INDEX ")
            self.append(item.name or item.autoname())
            self.execute()
        elif isinstance(item,constraint.ForeignKeyConstraint):
            pass    # SQLite doesn't use FKs

class SQLiteSchemaDropper(SQLiteConstraintDropper,sqlalchemy.ansisql.ANSISchemaDropper):
    pass

class SQLiteDialectChangeset(object):
    columngenerator = SQLiteColumnGenerator
    columndropper = SQLiteColumnDropper
    schemachanger = SQLiteSchemaChanger

    def schemadropper(self,*args,**params):
        return SQLiteSchemaDropper(*args,**params)

def _patch():
    util.prepend_base(sqlite.SQLiteDialect,SQLiteDialectChangeset)
    sqlite.SQLiteSchemaGenerator.__bases__ += (SQLiteConstraintGenerator,)
    #sqlite.SQLiteSchemaDropper.__bases__ += (SQLiteConstraintDropper,)
