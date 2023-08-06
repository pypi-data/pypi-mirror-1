from sqlalchemy import Table, Column, Integer, Text, MetaData, ForeignKey, create_engine
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy_validations import *

import re

class TestPresenceOf(object):
     def setup(self):
          global Person, session, metadata

          engine = create_engine('sqlite:///:memory:', echo=True)

          metadata = MetaData()
          person_table = Table('persons', metadata,
                              Column('id', Integer, primary_key=True),
                              Column('name', Text),
                              Column('phone', Text),
                              Column('age', Integer),
                              )

          metadata.bind = engine
          metadata.create_all()

          class Person(object):
               def __init__(self, name, phone, age):
                    self.name = name
                    self.phone = phone
                    self.age = age

                    def __repr__(self):
                         return "<Person('%s','%s','%d')>" % (self.name, self.phone, self.age)

          mapper(Person, person_table,
                 extension=[ Validator(presence_of('name')) ]
                 )
          Session = sessionmaker(bind=engine, autoflush=True, transactional=True)
          session = Session()

     def test_presence_of(self):
          foo = Person(None, '12345678', 22)
          session.save(foo)
          try:     
               session.flush()
               raise Exception('session.flush should have raised a ValidationException but it did not.')
          except ValidationException:
               pass
          
          foo.name = 'Foobar'
          
          session.flush()

     def teardown(self):
          session.clear()
          metadata.drop_all()

class TestRangeOf(object):
     def setup(self):
          global Person, session, metadata

          engine = create_engine('sqlite:///:memory:', echo=True)

          metadata = MetaData()
          person_table = Table('persons', metadata,
                              Column('id', Integer, primary_key=True),
                              Column('name', Text),
                              Column('phone', Text),
                              Column('age', Integer),
                              )

          metadata.bind = engine
          metadata.create_all()

          class Person(object):
               def __init__(self, name, phone, age):
                    self.name = name
                    self.phone = phone
                    self.age = age

                    def __repr__(self):
                         return "<Person('%s','%s','%d')>" % (self.name, self.phone, self.age)

          mapper(Person, person_table,
                 extension=[
                    Validator(range_of('age', 0, 150))
                    ]
                 )
          Session = sessionmaker(bind=engine, autoflush=True, transactional=True)
          session = Session()

     def test_range_of(self):
          foo = Person(None, '12345678', -1)
          session.save(foo)


          try:     
               session.flush()
               raise Exception('session.flush should have raised a ValidationException but it did not.')
          except ValidationException:
               pass
          
          foo.age = 200
          
          try:     
               session.flush()
               raise Exception('session.flush should have raised a ValidationException but it did not.')
          except ValidationException:
               pass

          foo.age = 42

          session.flush()

     def teardown(self):
          session.clear()
          metadata.drop_all()

class TestFormatOf(object):
     def setup(self):
          global Person, session, metadata

          engine = create_engine('sqlite:///:memory:', echo=True)

          metadata = MetaData()
          person_table = Table('persons', metadata,
                              Column('id', Integer, primary_key=True),
                              Column('name', Text),
                              Column('phone', Text),
                              Column('age', Integer),
                              )

          metadata.bind = engine
          metadata.create_all()

          class Person(object):
               def __init__(self, name, phone, age):
                    self.name = name
                    self.phone = phone
                    self.age = age

                    def __repr__(self):
                         return "<Person('%s','%s','%d')>" % (self.name, self.phone, self.age)

          mapper(Person, person_table,
                 extension=[
                    Validator(format_of('phone', re.compile(r'\d{4}-?\d{4}'))),
                    ]
                 )
          Session = sessionmaker(bind=engine, autoflush=True, transactional=True)
          session = Session()

     def test_format_of(self):
          foo = Person(None, '', -1)
          session.save(foo)

          try:     
               session.flush()
               raise Exception('session.flush should have raised a ValidationException but it did not.')
          except ValidationException:
               pass
          
          foo.phone = 'abcd-efgh'
          
          try:     
               session.flush()
               raise Exception('session.flush should have raised a ValidationException but it did not.')
          except ValidationException:
               pass

          foo.phone = '1234-5678'

          session.flush()

     def teardown(self):
          session.clear()
          metadata.drop_all()

class TestMultipleValidations(object):
     def setup(self):
          global Person, session, metadata

          engine = create_engine('sqlite:///:memory:', echo=True)

          metadata = MetaData()
          person_table = Table('persons', metadata,
                              Column('id', Integer, primary_key=True),
                              Column('name', Text),
                              Column('phone', Text),
                              Column('age', Integer),
                              )

          metadata.bind = engine
          metadata.create_all()

          class Person(object):
               def __init__(self, name, phone, age):
                    self.name = name
                    self.phone = phone
                    self.age = age

                    def __repr__(self):
                         return "<Person('%s','%s','%d')>" % (self.name, self.phone, self.age)

          mapper(Person, person_table,
                 extension=[
                    Validator(range_of('age', 0, 150), format_of('phone', re.compile(r'\d{4}-?\d{4}'))),
                    ]
                 )
          Session = sessionmaker(bind=engine, autoflush=True, transactional=True)
          session = Session()

     def test_multiple_validations(self):
          foo = Person(None, '', -1)
          session.save(foo)

          try:     
               session.flush()
               raise Exception('session.flush should have raised a ValidationException but it did not.')
          except ValidationException:
               pass
          
          foo.phone = 'abcd-efgh'
          
          try:     
               session.flush()
               raise Exception('session.flush should have raised a ValidationException but it did not.')
          except ValidationException:
               pass

          foo.phone = '1234-5678'

          try:     
               session.flush()
               raise Exception('session.flush should have raised a ValidationException but it did not.')
          except ValidationException:
               pass
          
          foo.age = 200
          
          try:     
               session.flush()
               raise Exception('session.flush should have raised a ValidationException but it did not.')
          except ValidationException:
               pass

          foo.age = 42
          session.flush()

     def teardown(self):
          session.clear()
          metadata.drop_all()
