#Load.py here you load the database structure and then load the data.

#------------------Connection String ------------------------------
#Import necesary items for database connection.
from sqlalchemy import create_engine

#[CHANGE]Here are examples on laoding few databases
#engine = create_engine('sqlite:///:memory:', echo=True)
#engine = create_engine('postgres://username:password@hostname:port/databasename', echo=True)
#engine = create_engine('mssql://username:password@hostname/databasename', echo=True)
#engine = create_engine('mysql://username:password@hostname:port/databasename', echo=True)

#We will use sqlite, until you are ready for production database. Comment out the sqlite code and uncomment your database when you are ready.
engine = create_engine('sqlite:///./devdata.db', echo=True)


#-------------------Connection Settings ----------------------------

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
import sqlalchemy

#engine.echo=True
engine.echo=False
metadata=sqlalchemy.MetaData(engine)

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import mapper

#Session = sessionmaker(bind=engine, autoflush=True, autocommit=True)
Session = sessionmaker(bind=engine, autoflush=True, transactional=True)
session = Session()


#----------------------Database Design ---------------------------
#Connected to a database




#[CHANGE] Python Class, just change the name to something unique(case sensitive). We will map this python class to the table we define below. It will make manipulating data much easier.
#If you are using vim editor you could change all of the names via this command, except # sign.
#:%s/MyTable/SomeOtherName/gc

class MyTable(object):
    def __init__(self, **kw):
        for key,value in kw.items():
            setattr(self, key, value)


#Table definition. Usually based on some file definition. We need to laod date modules if there is a date in a definition.
from datetime import datetime
import time


#You should put a description of the data definition below. Filename, todays date, etc.


#[CHANGE]change mytable word to something that describes your data.
#mytable_table -- is a table name in our program we will map it to python class above
#'mytable' - is the actual name of the table that will be in the database 
mytable_table = sqlalchemy.Table('mytable', metadata,
    sqlalchemy.Column('column_Sid', sqlalchemy.Integer, primary_key=True,info={"description":"AutoIncrement ID"}),
    sqlalchemy.Column('column1', sqlalchemy.Integer,info={"description":"column1"}),
    sqlalchemy.Column('column2', sqlalchemy.String(4),info={"description":"column2"}),
    sqlalchemy.Column('column3', sqlalchemy.Date,info={"description":"column3"}),
    sqlalchemy.Column('column4', sqlalchemy.Integer(2),info={"description":"column4"})
)


#---------------------Create table------------------------

#Dropping an existing tables if exists
metadata.drop_all(engine)

#recreating the table structure
metadata.create_all(engine)

#[CHANGE]We are mapping our table to our python class, so that later we can easly manipulate data via our python class
mapper(MyTable,mytable_table)
#Here we tell the session to save everything we did.
session.flush()

#---------------------Load Data-----------------------------
#Start loading your data below
#Here is a csv sample

import csv
#reader = csv.reader(open("../parse/somefile.txt"),delimiter="\t")  #tsv
reader = csv.reader(open("../parse/somefile.csv"))   #csv

#We are going to loop through file and add the data to database.
j=0
for column1,column2,column3,column4 in reader:
    #print column1,column2,column3,column4
    #This creates a record in database, and fills it in with data from csv.
    record=MyTable(column1=column1,column2=column2,column3=column3,column4=column4)
    #This adds it to the database session.    
    session.add(record)
    j+=1
    if j%10000==0:
        print 'saving %dth row' %j
        #Saving to db every 10,000 records
        session.flush()
session.flush()
session.commit()
print 'Commiting All Changes'


#loading 5 record, to test
session.query(MyTable).limit(5).all()
for i in y:
    print 'Getting 5 records'
    print  i.column1,i.column2,i.column3,i.column4

