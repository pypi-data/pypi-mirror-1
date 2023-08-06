from autorm.db.query import Query
from autorm.db import escape
from autorm.db.connection import autorm_db, Database
from autorm.validators import ValidatorChain
from autorm.fields import *
    
class ModelCache(object):
    models = {}
    
    def add(self, model):
        self.models[model.__name__] = model
        
    def get(self, model_name):
        return self.models[model_name]
   
cache = ModelCache()
    
class Empty:
    pass

class ModelBase(type):
    '''
    Metaclass for Model
    
    Sets up default table name and primary key
    Adds fields from table as attributes
    Creates ValidatorChains as necessary
    
    '''
    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return super(ModelBase, cls).__new__(cls, name, bases, attrs)
            
        new_class = type.__new__(cls, name, bases, attrs)
        
        if not getattr(new_class, 'Meta', None):
            new_class.Meta = Empty
        
        if not getattr(new_class.Meta, 'table', None):
            new_class.Meta.table = name.lower()
        new_class.Meta.table_safe = escape(new_class.Meta.table)
                
        if not getattr(new_class.Meta, 'objects', None):
            setattr(new_class, 'objects', BaseManager())
        else:
            setattr(new_class, 'objects', new_class.Meta.objects)

        new_class.objects.rclass = new_class
        
        
        # See cursor.description
        # http://www.python.org/dev/peps/pep-0249/
        if not hasattr(new_class, "db"):
            new_class.db = autorm_db
        #db = new_class.db
        
        defaults = {}
        if not getattr(new_class.Meta, 'fields', None):
            q = Query.raw_sql('SELECT * FROM %s LIMIT 1' % new_class.Meta.table_safe, db=new_class.db)
            new_class._fields = [Field(f[0]) for f in q.description]
            
            for field in getattr(new_class.Meta, 'field_overrides', []):
                if field.name not in new_class._fields:
                    raise Exception("No db column named %s in %s" % (field.name, new_class.table))
                new_class._fields[new_class._fields.index(field.name)] = field
            new_class.Meta.fields = new_class._fields
        else:
            new_class._fields = getattr(new_class.Meta, 'fields')

        field_validations = getattr(new_class.Meta, 'validations', {})
        field_map = {}
        for f in new_class._fields:
            field_map[f.name] = f
            validation = f.validators()
            if not validation: continue
            if f.name in field_validations:
                if type(field_validations[f.name]) == tuple:
                    field_validations[f.name] = list(field_validations[f.name])
                elif type(field_validations[f.name]) != list:            
                    field_validations[f.name] = [field_validations[f.name]]
                else:
                    field_validations[f.name].extend(validation)
            else:
                field_validations[f.name] = validation
        
        # cache a map of the fields
        new_class.Meta.field_map = field_map
        # Create function to loop over iterable validations
        if len(field_validations):
            new_class.Meta.validations = field_validations
        for k, v in field_validations.iteritems():
            if isinstance(v, (list, tuple)):
                new_class.Meta.validations[k] = ValidatorChain(*v)
        
        # TODO: fix, look at the fields
        # Assume id is the default 
        if not getattr(new_class.Meta, 'pk', None):
            new_class.Meta.pk = 'id'
        
        cache.add(new_class)
        return new_class
        
class BaseManager(object):
    def __init__(self, rclass=None):
        # this is set by the __new__ method of class
        self.rclass = rclass
    
    def get(self, pk):
        return self.query(**{self.rclass.Meta.pk: pk})[0]

    def query(self, **kwargs):
        'Returns Query object'
        return Query(model=self.rclass, conditions=kwargs)
    
    def cursor(self):
        c = Query.get_cursor(self.rclass.db)
        def row_factory(q, row):
            o = self.rclass()
            for col,v in zip(q.description, row):
                if col[0] in o._fields:
                    f = o._fields[o._fields.index(col[0])]
                    setattr(o, f.name, f.to_python(v))
                else:
                    setattr(o, col[0], v)
            return o
        c.row_factory = row_factory
        return c
        
    def create(self, *args, **kwargs):
        o = self.rclass(*args, **kwargs)
        o.save()
        return o
    
    def table_exists(self):
        """
        Given an AutORM model, check to see if its table exists.
        """
        try:
            s_sql = "SELECT * FROM %s LIMIT 1;" % self.rclass.Meta.table_safe
            Query.raw_sql(s_sql, db=self.rclass.db)
        except Exception:
            return False
    
        # if no exception, the table exists and we are done
        return True
    
    
    def create_table(self):
        """
        Create a table for an AutORM class.
        """
        if hasattr(self.rclass.Meta, 'create_sql'):
            s_create_sql = self.rclass.Meta.create_sql
        else:
            fields = []
            deferred = []
            for f in self.rclass._fields:
                if f.creation_deferred:
                    deferred.append(f.define(self.rclass.Meta.table))
                else:
                    fields.append(f.define())
                
            s_create_sql = """CREATE TABLE %s (%s); %s;""" % (self.rclass.Meta.table_safe, 
                                                            ", ".join(fields), ";".join(deferred))
        
        Query.begin(db=self.rclass.db)
        Query.raw_sqlscript(s_create_sql, db=self.rclass.db)
        Query.commit(db=self.rclass.db)
    
    
    def create_table_if_needed(self):
        """
        Check to see if an AutORM class has its table created; create if needed.
        """
        if not self.table_exists():
            self.create_table()

class Model(object):
    '''
    Allows for automatic attributes based on table columns.
    
    Syntax::
    
        from autorm.model import Model
        class MyModel(Model):
            class Meta:
                # If field is blank, this sets a default value on save
                defaults = {'field': 1}
            
                # Each validation must be callable
                # You may also place validations in a list or tuple which is
                # automatically converted int a ValidationChain
                validations = {'field': lambda v: v > 0}
            
                # Table name is lower-case model name by default
                # Or we can set the table name
                table = 'mytable'
        
        # Create new instance using args based on the order of columns
        m = MyModel(1, 'A string')
        
        # Or using kwargs
        m = MyModel(field=1, text='A string')
        
        # Saving inserts into the database (assuming it validates [see below])
        m.save()
        
        # Updating attributes
        m.field = 123
        
        # Updates database record
        m.save()
        
        # Deleting removes from the database 
        m.delete()
        
        # Purely saving with an improper value, checked against 
        # Model.Meta.validations[field_name] will raise Model.ValidationError
        m = MyModel(field=0)
        
        # 'ValidationError: Improper value "0" for "field"'
        m.save()
        
        # Or before saving we can check if it's valid
        if m.is_valid():
            m.save()
        else:
            # Do something to fix it here
        
        # Retrieval is simple using Model.get
        # Returns a Query object that can be sliced
        MyModel.get()
        
        # Returns a MyModel object with an id of 7
        m = MyModel.get(7)
        
        # Limits the query results using SQL's LIMIT clause
        # Returns a list of MyModel objects
        m = MyModel.get()[:5]   # LIMIT 0, 5
        m = MyModel.get()[10:15] # LIMIT 10, 5
        
        # We can get all objects by slicing, using list, or iterating
        m = MyModel.get()[:]
        m = list(MyModel.get())
        for m in MyModel.get():
            # do something here...
            
        # We can filter our Query
        m = MyModel.get(field=1)
        m = m.filter(another_field=2)
        
        # This is the same as
        m = MyModel.get(field=1, another_field=2)
        
        # Set the order by clause
        m = MyModel.get(field=1).order_by('field', 'DESC')
        # Removing the second argument defaults the order to ASC
        
    '''
    __metaclass__ = ModelBase
    
    debug = False

    def __init__(self, *args, **kwargs):
        'Allows setting of fields using kwargs'
        self.__dict__[self.Meta.pk] = None
        self.__dict__['_new_record'] = True
        [setattr(self, self._fields[i].name, arg) for i, arg in enumerate(args)]
        [setattr(self, k, v) for k, v in kwargs.iteritems()]
        self._changed = set()
        
    def __setattr__(self, name, value):
        'Records when fields have changed'
        if self._new_record is False and name != '_changed' and name in self._fields and hasattr(self, '_changed'):
            self._changed.add(self._fields[self._fields.index(name)])
        self.__dict__[name] = value
        
    def _get_pk(self):
        'Sets the current value of the primary key'
        return getattr(self, self.Meta.pk, None)

    def _set_pk(self, value):
        'Sets the primary key'
        return setattr(self, self.Meta.pk, value)    
        
    def _update(self):
        'Uses SQL UPDATE to update record'
        query = 'UPDATE %s SET ' % self.Meta.table_safe
        query += ', '.join(['%s = %s' % (escape(f.name), self.db.conn.placeholder) for f in self._changed])
        query += ' WHERE %s = %s ' % (escape(self.Meta.pk), self.db.conn.placeholder)
        
        values = [f.to_db(getattr(self, f.name)) for f in self._changed]
        values.append(self._get_pk())
        
        cursor = Query.raw_sql(query, values, self.db)
        
    def _new_save(self):
        'Uses SQL INSERT to create new record'
        # if pk field is set, we want to insert it too
        # if pk field is None, we want to auto-create it from lastrowid
        include_pk = True if self._get_pk() is not None else False
        if not hasattr(self.__class__, "_insert_stmt_cache_%s" % include_pk):
            fields=[
                escape(f.name) for f in self._fields 
                    if f.name != self.Meta.pk or include_pk
            ]
            
            placeholders = []
            for f in self._fields:
                if f.name == self.Meta.pk and not include_pk:
                    continue
                if f.sql_type == 'GEOMETRY':
                    placeholders.append("GeomFromText(%s, %d)" % (self.db.conn.placeholder, f.srid))
                else:
                    placeholders.append(self.db.conn.placeholder)
            
            query = 'INSERT INTO %s (%s) VALUES (%s)' % (
                   self.Meta.table_safe,
                   ', '.join(fields),
                   ', '.join(placeholders)
            )
            setattr(self.__class__, "_insert_stmt_cache_%s" % include_pk, query)
        else:
            query = getattr(self.__class__, "_insert_stmt_cache_%s" % include_pk)
            
        values = [f.to_db(getattr(self, f.name, None)) for f in self._fields
                      if f.name != self.Meta.pk or include_pk]    

        cursor = Query.raw_sql(query, values, self.db)
        
        if self._get_pk() is None:
            self._set_pk(cursor.lastrowid)

        return True
        
    def _get_defaults(self):
        'Sets attribute defaults based on ``defaults`` dict'
        for k, v in getattr(self.Meta, 'defaults', {}).iteritems():
            if not getattr(self, k, None):
                if callable(v):
                    v = v()
                setattr(self, k, v)
        
    def delete(self):
        'Deletes record from database'
        query = 'DELETE FROM %s WHERE %s = %s' % (self.Meta.table_safe, self.Meta.pk, self.db.conn.placeholder)
        values = [getattr(self, self.Meta.pk)]
        Query.raw_sql(query, values, self.db)
        return True
        
    def is_valid(self):
        'Returns boolean on whether all ``validations`` pass'
        try:
            self._validate()
            return True
        except Model.ValidationError:
            return False
    
    def _validate(self):
        'Tests all ``validations``, raises ``Model.ValidationError``'
        for k, v in getattr(self.Meta, 'validations', {}).iteritems():
            assert callable(v), 'The validator must be callable'
            value = getattr(self, k)
            if not v(self, value):
                raise Model.ValidationError, 'Improper value "%s" for "%s"' % (value, k)
        
    def save(self):
        'Sets defaults, validates and inserts into or updates database'
        self._get_defaults()
        self._validate()
        if self._new_record:
            self._new_save()
            self._new_record = False
            return True
        else:
            return self._update()
        
    def items(self):
        for f in self._fields:
            yield f.name, getattr(self, f.name, None)
        
    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, 
                           ", ".join(["%s=%s" % (k,v) for k,v in self.items()]))

        
    class ValidationError(Exception):
        pass
