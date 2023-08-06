# -*- coding: utf-8 -*- 
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
    name='sqlalchemy_elixir_validations',
    version='0.1.1',
    description='Simple model validations for Elixir and Sqlalchemy',
    author='Leandro Lameiro & Bartosz Radaczynski',
    author_email='lameiro@gmail.com',
    url='http://www.bitbucket.org/radaczynski/sqlalchemy_elixir_validations',
    py_modules=['sqlalchemy_validations','elixir_validations'],
    long_description="""
SQLAlchemy and Elixir validations
=================================

Provide a set of simple yet useful validations for the models:
Sqlalchemy:
-----------
from sqlalchemy_validations import *
people_table = Table(....)
class Person(object)
    pass
    
mapper(Person, people_table,
       extension=[Validator(
                            range_of('age', 0, 150),
                            format_of('phone', re.compile(r'\d{4}-?\d{4}'))
                            numericality_of('foo','bar','some_next_field')
                           )
                 ]
      )
      
Elixir:
-------
from elixir_validations import *
class Person(Entity):
    username=Field(Unicode(30),nullable=False,index=True)
    email=Field(Unicode,nullable=False)
    age=Field(Integer,nullable=False)
    
    validates_uniqueness_of('username')
    validates_presence_of('username', 'email')
    validates_format_of('email',re.compile("[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])"))
    validates_numericality_of('age',integer_only = True)

""",
    classifiers=[
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python",
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "Topic :: Internet",
          "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='sqlalchemy elixir validations',
    license='MIT',
    packages=find_packages(),
    install_requires=[
            'SQLAlchemy>=0.5.0beta3',
    ],
    )
