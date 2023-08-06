#Create Engine
from sqlalchemy import create_engine
#engine = create_engine('sqlite:///:memory:', echo=True)
#engine = create_engine('postgres://username:password@hostname:port/databasename', echo=True)
#engine = create_engine('postgres://username:password@hostname:port/databasename', echo=True)
#engine = create_engine('mysql://username:password@hostname:port/databasename', echo=True)
engine = create_engine('sqlite:///./devdata.db', echo=True)

#Define Table
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
metadata = MetaData()
users_table = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('fullname', String),
    Column('password', String)
)
foo_table = Table("Foo", metadata,
     Column("id", Integer, primary_key=True),
     Column("bar", String(255), nullable=False),
     )

#Create Table
metadata.create_all(engine) 

#Create Python Class to be Mapped
class Foo(object):
    def __init__(self, **kw):
        """automatically mapping attributes"""
        for key, value in kw.iteritems():
            setattr(self, key, value)

#Setup the Mapping
from sqlalchemy.orm import mapper, relation
mapper(Foo, foo_table)


 
