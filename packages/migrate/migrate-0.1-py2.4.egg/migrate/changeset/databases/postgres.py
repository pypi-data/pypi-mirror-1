from migrate.changeset import ansisql,util,constraint
from sqlalchemy.databases import postgres
import sqlalchemy

class PGColumnGenerator(postgres.PGSchemaGenerator,ansisql.ANSIColumnGenerator):
#class PGColumnGenerator(ansisql.ANSIColumnGenerator,postgres.PGSchemaGenerator):
    pass
class PGColumnDropper(ansisql.ANSIColumnDropper):
    pass
class PGSchemaChanger(ansisql.ANSISchemaChanger):
    pass
class PGConstraintGenerator(ansisql.ANSIConstraintGenerator):
    pass
class PGConstraintDropper(ansisql.ANSIConstraintDropper):
    pass

class PGDialectChangeset(object):
    columngenerator = PGColumnGenerator
    columndropper = PGColumnDropper
    schemachanger = PGSchemaChanger

    constraint_types = {
        "PRIMARY KEY":constraint.PrimaryKeyConstraint,
        "FOREIGN KEY":constraint.ForeignKeyConstraint,
    }

    def _reflectconstraints_init(self,connection,table_name):
        q = """select constraint_name,constraint_type
        from information_schema.table_constraints 
        where lower(table_name) = lower(%(table)s)"""
        constraints_data= connection.execute(q,dict(table=table_name))
        # Build constraints
        ret = sqlalchemy.util.OrderedDict()
        for consdata in constraints_data:
            type = consdata['constraint_type']
            name = consdata['constraint_name']
            cls = self.constraint_types.get(type,constraint.Constraint)
            cons = cls(name=name)
            ret[name] = cons
        return ret
    def _reflectconstraints_columns(self,connection,items,table):
        # If a table object is given, organize the columns too
        q = """select constraint_name,column_name
        from information_schema.key_column_usage
        where lower(table_name) = lower(%(table)s)"""
        constraint_cols_data = connection.execute(q,dict(table=table.name))
        # Organize columns by constraint name
        cons_cols = dict()
        for cons_name, col_name in constraint_cols_data:
            if cons_name not in cons_cols:
                cons_cols[cons_name] = list()
            col = getattr(table.c,col_name)
            cons_cols[cons_name].append(col)
        # Assign table,cols to constraints
        for cons_name,cols in cons_cols.iteritems():
            cons = items[cons_name]
            cons.set_columns(*cols)
            cons.table = table
        return items
    def _reflectconstraints_references(self,connection,items):
        q = """select table_name,column_name
        from information_schema.constraint_column_usage
        where lower(constraint_name) = lower(%(name)s)"""
        meta = sqlalchemy.BoundMetaData(connection.engine)
        for item in items:
            if not isinstance(item,constraint.ForeignKeyConstraint):
                # only foreign keys have references to load
                continue
            print item
            data = connection.execute(q,dict(name=item.name))
            table = None
            for table_name,column_name in data:
                if table is None:
                    table = sqlalchemy.Table(table_name,meta,autoload=True)
                column = getattr(table.c,column_name)
                item.references.append(column)
        return items
                    
        # Organize columns by constraint name
        cons_cols = dict()
        for cons_name, col_name in constraint_cols_data:
            if cons_name not in cons_cols:
                cons_cols[cons_name] = list()
            col = getattr(table.c,col_name)
            cons_cols[cons_name].append(col)
        # Assign table,cols to constraints
        for cons_name,cols in cons_cols.iteritems():
            cons = items[cons_name]
            cons.set_columns(*cols)
            cons.table = table
        return items

    def reflectconstraints(self,connection,table):
        if isinstance(table,basestring):
            table_name = table
            table = None # no table object
        else:
            table_name = table.name
        ret = self._reflectconstraints_init(connection,table_name)

        if table is not None:
            ret = self._reflectconstraints_columns(connection,ret,table)
            ret = self._reflectconstraints_references(connection,ret)
        return ret

def _patch():
    #postgres.PGDialect.columngenerator = PGColumnGenerator
    #postgres.PGDialect.__bases__ += (PGDialectChangeset,)
    util.prepend_base(postgres.PGDialect,PGDialectChangeset)
    postgres.PGSchemaGenerator.__bases__ += (PGConstraintGenerator,)
    postgres.PGSchemaDropper.__bases__ += (PGConstraintDropper,)
