from autumn.db.connection import db
from autumn.model import Model
from autumn.db.relations import ForeignKey, OneToMany
import datetime

#db.connect('sqlite3', '/tmp/example.db')
db.connect('mysql', user='root', db='superjared')
    
class Author(Model):
    books = OneToMany('Book')
    
    class Meta:
        defaults = {'bio': 'No bio available'}
        validations = {'first_name': lambda self, v: len(v) > 1}
    
class Book(Model):
    author = ForeignKey(Author)
    
    class Meta:
        table = 'books'
