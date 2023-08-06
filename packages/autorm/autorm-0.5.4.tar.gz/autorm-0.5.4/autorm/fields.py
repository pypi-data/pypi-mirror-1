import json
import cPickle as pickle
from cStringIO import StringIO
from autorm.validators import NotNull
import datetime
from autorm.db import escape
from autorm.db.query import OPERATORS

class FieldBase(object):
    def __init__(self, name, default=None, index=False, notnull=False, primary_key=False, sql_type="TEXT"):
        self.name = name
        self.default = default
        self.index = index
        self.notnull = notnull
        self.primary_key = primary_key
        self.sql_type = sql_type
        self.creation_deferred = False
        
    def __eq__(self, b):
        if isinstance(b, FieldBase):
            return self.name == b.name
        if type(b) == str:
            return self.name == b
        return False
    
    def to_python(self, value):
        return value
    
    def to_db(self, value):
        return value
    
    def sql_conditional(self, value, operator, placeholder):
        if operator in ('notin','in'):
            if type(value) not in (list, tuple):
                value = (value,)
            return "%s %s (%s)" % (escape(self.name), OPERATORS[operator],",".join([placeholder]*len(value))), map(self.to_db,value)  
        else:
            return "%s %s %s" % (escape(self.name), OPERATORS[operator], placeholder), self.to_db(value)
    
    def define(self):
        return "%s %s%s%s" % (self.name, 
                              self.sql_type,
                              self.default != None and " DEFAULT %s" % self.to_db(self.default) or "", 
                              self.notnull and " NOT NULL" or "")
        
    def validators(self):
        if self.notnull:
            return [NotNull()]
        return None
    
    
class Field(FieldBase):
    pass

class TextField(Field):
    def __init__(self, name, length=None, **kwargs):
        if not length:
            kwargs['sql_type'] = 'TEXT'
        else: 
            kwargs['sql_type'] = 'VARCHAR(%d)' % length
        super(TextField, self).__init__(name, **kwargs)

class IntegerField(Field):
    def __init__(self, name, **kwargs):
        kwargs['sql_type'] = 'INTEGER'
        super(IntegerField, self).__init__(name, **kwargs)

class FloatField(Field):
    def __init__(self, name, **kwargs):
        kwargs['sql_type'] = 'FLOAT'
        super(FloatField, self).__init__(name, **kwargs)
        
class IdField(Field):
    def __init__(self, name, auto_increment=True):
        super(IdField, self).__init__(name, sql_type= ("INTEGER PRIMARY KEY" + (auto_increment and " AUTOINCREMENT" or "")))

class BoolField(Field):
    def __init__(self, name, **kwargs):
        kwargs['sql_type'] = 'INTEGER'
        super(BoolField, self).__init__(name, **kwargs)

    def to_python(self, value):
        if value == None: return None
        if value == 0:
            return False
        return True
    
    def to_db(self, value):
        if value == None: return None
        if value:
            return 1
        return 0

class ISODateField(Field):
    def __init__(self, name, **kwargs):
        kwargs['sql_type'] = 'DATE'
        super(ISODateField, self).__init__(name, **kwargs)
  
    def to_python(self, value):
        if value == None: return None
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    
    def to_db(self, value):
        if value == None: return None
        return value.strftime("%Y-%m-%d")

class ISODateTimeField(Field):
    def __init__(self, name, **kwargs):
        kwargs['sql_type'] = 'DATE TIME'
        super(ISODateTimeField, self).__init__(name, **kwargs)
  
    def to_python(self, value):
        if value == None: return None
        return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    
    def to_db(self, value):
        if value == None: return None
        return value.strftime("%Y-%m-%d %H:%M:%S")
    
class JSONField(Field):
    def to_python(self, dbvalue):
        if not dbvalue: return None
        return json.loads(dbvalue)
    
    def to_db(self, pyvalue):
        if not pyvalue: return None
        return json.dumps(pyvalue)

class PickleField(Field):
    def to_python(self, dbvalue):
        if not dbvalue: return None
        return pickle.loads(str(dbvalue))
    
    def to_db(self, pyvalue):
        if not pyvalue: return None
        return pickle.dumps(pyvalue)

try:
    # we prefer the django GEOS implementation
    import django.contrib.gis.geos
    HAS_DJGEOS = True
except:
    HAS_DJGEOS = False

class GeometryField(Field):
    GEOM_OPERATORS = {\
        "eq": "Equals(%s, %s)",
        "bbintersects":"MbrIntersects(%s, %s)",
        "intersects": "Intersects(%s, %s)",
        "contains": "Contains(%s, %s)",
        "within": "Within(%s, %s)",
        "crosses": "Crosses(%s, %s)",
    }
    
    def __init__(self, name, **kwargs):
        kwargs['sql_type'] = 'GEOMETRY'
        self.srid = kwargs.get('srid',-1)
        del kwargs['srid']
        super(GeometryField, self).__init__(name, **kwargs)
        self.creation_deferred = True
        self.geom_type = kwargs.get('geom_type','GEOMETRY')
        self.dimensions = 2

    def to_python(self, dbvalue):
        if not dbvalue: return None
        if HAS_DJGEOS:
            return django.contrib.gis.geos.GEOSGeometry(dbvalue)
        else: return dbvalue # as WKT

    def to_db(self, pyvalue):
        if not pyvalue: return None
        if HAS_DJGEOS:
            if isinstance(pyvalue, django.contrib.gis.geos.GEOSGeometry): 
                pyvalue = pyvalue.wkt
        return pyvalue # assumed to be WKT
    
    def sql_conditional(self, value, operator, placeholder):
        srid = None
        if HAS_DJGEOS:
            srid = value.srid
        if not srid:
            srid = self.srid
                
        return self.GEOM_OPERATORS[operator] % (escape(self.name),
                                           "GeomFromText(%s, %d)" % (placeholder, self.srid)), self.to_db(value)
    
    def define(self, table_name):
        return "SELECT AddGeometryColumn('%s', '%s', %s, '%s', %d); SELECT CreateSpatialIndex('%s', '%s')" % \
            (table_name, 
             self.name,
             self.srid,
             self.geom_type,
             self.dimensions,
             table_name,
             self.name) 

        