# AutORM, fork of Autumn, a Python ORM

This is a derivative project of Autumn [Autumn](http://github.com/JaredKuolt/autumn/tree).  It adds a few features: Fields (e.g. type converters, validation), query condition modifiers (less than, etc.), a few Django conventions (e.g. Model.objects.*), table creation from models, and ... TBD. Why Yet-[Yet Another Python ORM](http://superjared.com/entry/yet-another-python-orm/)? For the same reasons Jared Kuolt built the original Autumn ORM, but my use cases and preferences are slightly different.  I built my own system for use with sqlite that had much in common with Autumn, and a number of other features I needed, but ran into threading issues, so I merged the two projects as AutORM. Many thanks to him for the seed.

## What is Autumn (and by extension, AutORM)? 

Autumn exists as a super-lightweight Object-relational mapper (ORM) for Python. 
It’s an alternative to [SQLObject](http://www.sqlobject.org/), 
[SQLAlchemy](http://www.sqlalchemy.org/), [Storm](https://storm.canonical.com/),
etc. Perhaps the biggest difference is the ability for automatic population of fields as 
attributes (see the example below).

It is released under the MIT License (see LICENSE file for details).

This project is still under development.

## SQLite Example
MySQL theoretically supported, but not tested.

Assuming these tables:

    DROP TABLE IF EXISTS author;
    CREATE TABLE author (
        id INTEGER PRIMARY KEY autoincrement,
        first_name VARCHAR(40) NOT NULL,
        last_name VARCHAR(40) NOT NULL,
        bio TEXT,
        some_json_data TEXT
    );
    DROP TABLE IF EXISTS books;
    CREATE TABLE books (
        id INTEGER PRIMARY KEY autoincrement,
        title VARCHAR(255),
        other_json_data TEXT,
        author_id INT(11),
        FOREIGN KEY (author_id) REFERENCES author(id)
    );

We setup our objects like so:

	from autorm.db.connection import autorm_db
	from autorm.db.query import Query
	from autorm.model import Model
	from autorm.fields import *
	from autorm.db.relations import ForeignKey, OneToMany
	import datetime
	
	
	# This model's fields are defined explicitly, and does not need 
	# a connection on class creation.
	class Author(Model):
	    books = OneToMany('Book')
	
	    class Meta:
	        defaults = {'bio': 'No bio available'}
	        validations = {'first_name': lambda self, v: len(v) > 1}
	        # do not inspect the database, use these fields to define the columns
	        fields = [IdField('id'),
	                  TextField('first_name', notnull=True), TextField('last_name', notnull=True), 
	                  TextField('bio'),
	                  JSONField('some_json_data')]
	
	autorm_db.conn.connect('sqlite3', ':memory:')
	
	# let's create a table for the model above:
	Author.objects.create_table()
	
	# This model's fields are derived via introspecting the database. So, you need
	# a connection and a table.
	Query.raw_sqlscript("""
	    DROP TABLE IF EXISTS books;
	    CREATE TABLE books (
	        id INTEGER PRIMARY KEY autoincrement,
	        title VARCHAR(255),
	        other_json_data TEXT,
	        author_id INT(11),
	        FOREIGN KEY (author_id) REFERENCES author(id)
	    );
	""")
	
	class Book(Model):
	    author = ForeignKey(Author)
	
	    class Meta:
	        table = 'books'
	        # inspect the database to get field names, 
	        # use the default field type (no-op) for all the columns, except this one:
	        field_overrides = [JSONField('other_json_data')]
	
Now we can create, retrieve, update and delete entries in our database.

### Creation

	james = Author(first_name='James', last_name='Joyce', some_json_data={'key':'value'})
	james.save()
	
	u = Book(title='Ulysses', author_id=james.id)
	u.save()

### Retrieval

	# get by primary key
	a = Author.objects.get(1)
	# or
	a = Author.objects.query(id=1)[0]
	# or 
    a = Author.objects.query(first_name='James', last_name='Joyce').order_by('first_name')[0]
	assert a.first_name == 'James'
	assert len(a.books) == 1      # Returns list of author's books
	assert james.some_json_data['key'] == a.some_json_data['key']

	# Returns a list, using LIMIT based on slice
	a = Author.objects.query()[:10]   # LIMIT 0, 10
	a = Author.objects.query()[20:30] # LIMIT 20, 10

### Updating

	a = Author.objects.get(1)
	a.bio = 'What a crazy guy! Hard to read but... wow!'
	a.save()

### Deleting

	a.delete()
	
### Spatialite and Geometry Support

Basic support for GEOMETRY fields are supported, but sophisticated queries must be done manual.  Proper support depends on django.contrib.gis.geos.

	from autorm.db.connection import autorm_db
	from autorm.db.query import Query
	from autorm.model import Model
	from autorm.fields import *
	from autorm.db.relations import ForeignKey, OneToMany
	
	import autorm
	    
	from django.contrib.gis.geos import Point
	
	class Manifest(Model):
	    class Meta:
	        # do not inspect the database, use these fields to define the columns
	        
	        fields = [TextField('name', notnull=True),
	                  GeometryField('the_geom', notnull=True, srid=4326)]
	        
	
	
    autorm_db.conn.connect('spatialite', ":memory:")
    autorm_db.conn.b_debug = True
    Manifest.objects.create_table()
    
    Manifest(name='my poi', the_geom=Point(45,45)).save()

    print "Getting geom:" ,Manifest.objects.query()[0].the_geom
    print list(Manifest.objects.query(the_geom = Point(45,45)))
	    