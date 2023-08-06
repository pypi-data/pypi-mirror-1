from autorm.db.connection import autorm_db
from autorm.model import Model
from autorm.fields import *
from autorm.db.query import Query

from autorm.db.relations import ForeignKey, OneToMany
from autorm import validators
import datetime

#autorm_db.conn.connect('sqlite3', '/tmp/example.db')
#autorm_db.conn.connect('mysql', user='root', db='autorm')

#-----------------------------
# Create the test DB before creating the models, because we want to test introspection on one

autorm_db.conn.connect('sqlite3', ':memory:')
autorm_db.conn.b_debug = True

sqlite_create = """
 DROP TABLE IF EXISTS author;
 DROP TABLE IF EXISTS books;
 CREATE TABLE author (
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   first_name VARCHAR(40) NOT NULL,
   last_name VARCHAR(40) NOT NULL,
   bio TEXT
 );
 CREATE TABLE books (
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   title VARCHAR(255),
   author_id INT(11),
   json_data TEXT,
   FOREIGN KEY (author_id) REFERENCES author(id)
 );
"""
#autorm_db.conn.connect('sqlite3', ':memory:')
Query.raw_sqlscript(sqlite_create)


class Author(Model):
    books = OneToMany('Book')
    
    class Meta:
        defaults = {'bio': 'No bio available'}
        validations = {'first_name': validators.Length(),
                       'last_name': (validators.Length(), lambda obj,x: x != 'BadGuy!')}
        
        fields = [IdField('id'), Field('first_name'), Field('last_name'), TextField('bio')]
    
class Book(Model):
    author = ForeignKey(Author)
    
    class Meta:
        table = 'books'
        field_overrides = [JSONField('json_data')]
