import sqlalchemy

class Constraint(sqlalchemy.schema.SchemaItem):
    def __new__(cls,*args,**kwargs):
        if kwargs.pop('autoload',None):
            autoload_with = kwargs.pop('autoload_with',None)
            name = kwargs.pop('name',None)
            table = kwargs.pop('table',None)
            engine= kwargs.pop('engine',None)
            connection = kwargs.pop('connection',None)
            ret = cls.reflect(table,name,engine=engine,connection=connection,
                *args,**kwargs)
            ret._init = True
        else:
            ret = super(Constraint,cls).__new__(cls,*args,**kwargs)
            ret._init = False
        return ret
    def __init__(self,*args,**kwargs):
        if self._init: return # init done in __new__
        self.name = kwargs.pop('name',None)
        self.table = kwargs.pop('table',None)

        self.set_columns(*args)
        if self.table is None:
            self.table = self._get_table_from_cols(self.columns)

    def set_columns(self,*cols):
        self.columns = sqlalchemy.util.OrderedProperties()
        for col in cols:
            self.columns[col.name] = col

    @classmethod
    def _get_table_from_cols(cls,cols):
        ret = None
        for col in cols:
            if col.table is not None:
                ret = col.table
                break
        return ret
    
    def create(self,engine=None):
        if engine is None:
            engine = self.engine
        engine.create(self)
    def drop(self,engine=None):
        if engine is None:
            engine = self.engine
        engine.drop(self)
    def accept_schema_visitor(self,visitor):
        return visitor.visit_constraint(self)
    def get_cons_spec(self):
        raise NotImplementedError()

    @classmethod
    def reflect(cls,table,name,*p,**k):
        # This could be more efficient, but it's not a big deal
        return cls.reflectconstraints(table,*p,**k)[name]

    @classmethod
    def reflectconstraints(cls,table,engine=None,connection=None):
        """Return all of an existing table's constraints"""
        if engine is None:
            if connection is None:
                engine = table.engine
            else:
                engine = connection.engine
        if connection is None:
            conn = engine.contextual_connect()
        #if isinstance(table,basestring):
        #    table_name = table
        #else:
        #    table_name = table.name
        try:
            ret = engine.dialect.reflectconstraints(conn,table)
            # Set table, if possible
            #if not isinstance(table,basestring):
            #    for c in ret.values():
            #        c.table = table
            return ret
        finally:
            if connection is None:
                conn.close()

    def autoname(self):
        raise NotImplementedError()

    def _get_engine(self):
        return self.table.engine
    engine = property(_get_engine)
    c = property(lambda self: self.columns)
    def _get_name(self):
        ret = getattr(self,'_name',None)
        if ret is None:
            ret = self.autoname()
        return ret
    def _set_name(self,value):
        self._name = value
    name = property(_get_name,_set_name)

class PrimaryKeyConstraint(Constraint):
    def __init__(self,*args,**kwargs):
        """Given a list of column objects, create a PK constraint.
        May create as 
            PrimaryKeyConstraint("name",Column(),..)
            PrimaryKeyConstraint(Column(),..,name="name")
        """
        if self._init: return # init done in __new__
        args = list(args)
        if len(args) > 0 and isinstance(args[0],basestring):
            if 'name' not in kwargs:
                kwargs['name'] = args.pop(0)
        super(PrimaryKeyConstraint,self).__init__(*args,**kwargs)
    @classmethod
    def reflect(cls,table,name=None,*p,**k):
        if isinstance(table,basestring):
            # Introspect table from name
            engine = k.pop('engine',None)
            meta = sqlalchemy.BoundMetaData(engine)
            table = sqlalchemy.Table(table,meta,autoload=True)
        constraints = cls.reflectconstraints(table,*p,**k)
        if name is not None:
            ret = constraints[name]
        else:
            # There's only one PK column; find it
            ret = None
            for cons in constraints.values():
                if isinstance(cons,cls):
                    ret = cons
                    break
        return ret
    def autoname(self):
        """Mimic the database's automatic constraint names"""
        ret = "%(table)s_pkey"%dict(
            table=self.table.name,
        )
        return ret

class ForeignKeyConstraint(Constraint):
    def __init__(self,*p,**k):
        super(ForeignKeyConstraint,self).__init__(*p,**k)
        reflist = k.pop('references',None)
        if reflist is None:
            reflist = [c.foreign_key.column for c in self.columns]
        self.references = sqlalchemy.util.OrderedDict()
        for colname,reference in zip(self.columns.keys(),reflist):
            self.references[colname] = reference
    @staticmethod
    def _col_to_colname(col):
        if isinstance(col,basestring):
            ret = col
        else:
            ret = col.name
        return ret
    @classmethod
    def reflect(cls,table=None,name=None,*cols,**k):
        if table is None:
            # Table implied by cols (maybe)
            table = cls._get_table_from_cols(cols)
        elif isinstance(table,basestring):
            # Table name/engine given
            engine = k.get('engine',None)
            if engine is None:
                engine = k.get('connection').engine
            meta = sqlalchemy.BoundMetaData(engine)
            table = sqlalchemy.Table(table,meta,autoload=True)
        constraints = cls.reflectconstraints(table,
            engine=k.pop('engine',None),connection=k.pop('connection',None))
        if name is not None:
            ret = constraints[name]
        else:
            # We must be given at least one column; find matching constraint 
            ret = None
            col_names = [cls._col_to_colname(c) for c in cols]
            col_names.sort()
            for cons in constraints.values():
                if not isinstance(cons,cls):
                    continue
                cons_col_names = [c.name for c in cons.columns]
                cons_col_names.sort()
                if cons_col_names == col_names:
                    ret = cons
                    break
        return ret

    def autoname(self):
        """Mimic the database's automatic constraint names"""
        ret = "%(table)s_%(ref_table)s_fkey"%dict(
            table=self.table.name,
            ref_table=self.ref_table.name,
        )
        return ret

    def _get_ref_table(self):
        return self._get_table_from_cols(self.references.values())
    ref_table = property(_get_ref_table)
