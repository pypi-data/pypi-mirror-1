from autumn.db.connection import db
from autumn.model import Model
from autumn.db.relations import ForeignKey, OneToMany
from autumn import validators
import datetime

#db.connect('sqlite3', '/tmp/example.db')
db.connect('mysql', user='root', db='superjared')
    
class Author(Model):
    books = OneToMany('Book')
    
    class Meta:
        defaults = {'bio': 'No bio available'}
        validations = {'first_name': validators.Length(),
                       'last_name': (validators.Length(), lambda x: x != 'BadGuy!')}
    
class Book(Model):
    author = ForeignKey(Author)
    
    class Meta:
        table = 'books'
