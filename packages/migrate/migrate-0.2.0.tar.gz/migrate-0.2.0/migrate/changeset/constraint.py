import sqlalchemy
from sqlalchemy import schema

class ConstraintChangeset(object):
    def _normalize_columns(self,cols,fullname=False):
        """Given: column objects or names; return col names and (maybe) a table"""
        colnames = []
        table = None
        for col in cols:
            if isinstance(col,schema.Column):
                if col.table is not None and table is None:
                    table = col.table
                if fullname:
                    col = '.'.join((col.table.name,col.name))
                else:
                    col = col.name
            colnames.append(col)
        return colnames,table
    def create(self,engine=None):
        if engine is None:
            engine = self.engine
        engine.create(self)
    def drop(self,engine=None):
        if engine is None:
            engine = self.engine
        #if self.name is None:
        #    self.name = self.autoname()
        engine.drop(self)
    def _derived_metadata(self):
        return self.table._derived_metadata()
    def accept_schema_visitor(self,visitor):
        return visitor.visit_constraint(self)
    def autoname(self):
        raise NotImplementedError()
    
class PrimaryKeyConstraint(ConstraintChangeset,schema.PrimaryKeyConstraint):
    def __init__(self,*cols,**kwargs):
        colnames,table = self._normalize_columns(cols)
        table = kwargs.pop('table',table)
        super(PrimaryKeyConstraint,self).__init__(*colnames,**kwargs)
        if table is not None:
            self._set_parent(table)

    def _set_parent(self,table):
        self.table = table
        return super(ConstraintChangeset,self)._set_parent(table)
    def autoname(self):
        """Mimic the database's automatic constraint names"""
        ret = "%(table)s_pkey"%dict(
            table=self.table.name,
        )
        return ret

class ForeignKeyConstraint(ConstraintChangeset,schema.ForeignKeyConstraint):
    def __init__(self,columns,refcolumns,*p,**k):
        colnames,table = self._normalize_columns(columns)
        table = k.pop('table',table)
        refcolnames,reftable = self._normalize_columns(refcolumns,fullname=True)
        super(ForeignKeyConstraint,self).__init__(colnames,refcolnames,*p,**k)
        if table is not None:
            self._set_parent(table)

    def _get_referenced(self):
        return [e.column for e in self.elements]
    referenced = property(_get_referenced)

    def _get_reftable(self):
        return self.referenced[0].table
    reftable = property(_get_reftable)
        
    def autoname(self):
        """Mimic the database's automatic constraint names"""
        ret = "%(table)s_%(reftable)s_fkey"%dict(
            table=self.table.name,
            reftable=self.reftable.name,
        )
        return ret

def _patch():
    pass
