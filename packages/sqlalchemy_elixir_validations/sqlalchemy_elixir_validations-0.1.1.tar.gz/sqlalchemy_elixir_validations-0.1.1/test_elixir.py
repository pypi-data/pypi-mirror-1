from elixir import *
from elixir_validations import *
 
import re

def setup():
    metadata.bind = 'sqlite:///'
    metadata.bind.echo = True

def teardown():
    pass

class TestPresenceOf(object):
    def setup(self):
        global Person
        
        class Person(Entity):
            name  = Field(Text)
            phone = Field(Text)
            age   = Field(Integer)
        
            validates_presence_of('name')

        setup_all(True)
        create_all()
    
    def teardown(self):
        drop_all()
        session.clear()
        cleanup_all()
    
    def test_presence_of(self):    
        lameiro = Person(phone='1234-5678', age=22)

        try:
            session.flush();
            raise Exception('Flush should have raised an Exception')
        except ValidationException:
            pass
        
        lameiro.name = 'Leandro Lameiro'
        session.flush();

class TestFormatOf(object):
    def setup(self):
        global Person
        
        class Person(Entity):
            name  = Field(Text)
            phone = Field(Text)
            age   = Field(Integer)
        
            validates_format_of('phone', re.compile(r'\d{4}-?\d{4}'))

        setup_all(True)
        create_all()
    
    def teardown(self):
        drop_all()
        session.clear()
        cleanup_all()
    
    def test_format_of(self):    
        lameiro = Person(phone='00-5678')

        try:
            session.flush();
            raise Exception('Flush should have raised an Exception')
        except ValidationException:
            pass        
        
        lameiro.phone = '1234-5678'
        session.flush();
        
        lameiro.phone = '12345678'
        session.flush();

class TestRangeOf(object):
    def setup(self):
        global Person
        
        class Person(Entity):
            name  = Field(Text)
            phone = Field(Text)
            age   = Field(Integer)
        
            validates_range_of('age', 0, 150)

        setup_all(True)
        create_all()
    
    def teardown(self):
        drop_all()
        session.clear()
        cleanup_all()
    
    def test_range_of(self):    
        lameiro = Person(age=1000)

        try:
            session.flush();
            raise Exception('Flush should have raised an Exception')
        except ValidationException:
            pass        
        
        lameiro.age = 22
        session.flush()
        
        lameiro.age = 0
        session.flush()
        
        lameiro.age = 150
        session.flush()
        
