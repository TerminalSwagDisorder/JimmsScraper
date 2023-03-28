# File name: database.py
# Auth: Benjamin Willför/TerminalSwagDisorder & Sami Wazni
# Desc: File currently in development containing code for creating a database

import os
import sqlite3
import itertools
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import ColumnClause
from sqlalchemy.sql import table, column, select, update, insert, delete, text
from sqlalchemy.ext.declarative import declarative_base

fPath = os.path.abspath(os.path.realpath(__file__))
dPath = os.path.dirname(fPath)
finPath = dPath + "\\database"

# Create database folder if it does not exist
if not os.path.exists(finPath):
	os.makedirs(finPath)

engine = create_engine("sqlite:///" + finPath + "\\pcbuildwebsite_db.db", echo=True, pool_pre_ping=True)
Session = sessionmaker(bind=engine)
session = Session()

# Define metadata information
metadata = MetaData()

main_parts = ["cpu", "gpu", "cooler", "motherboard", "memory", "storage", "psu", "case"]

# Part of SQLAlchemy
Base = declarative_base()
# Create table in database	 
class UniversalComponents(Base):
	__abstract__ = True
	ID = Column(Integer, primary_key=True, autoincrement=True)
	Name = Column(Text)
	Manufacturer = Column(Text)
	Price = Column(Text)
	Url = Column(Text)

class PSU(UniversalComponents):
	__tablename__ = 'psu'
	is_ATX12V = Column("is_ATX12V", Text)
	Dimensions = Column("Dimensions", Text)
	
class Case(UniversalComponents):
	__tablename__ = 'case'
	Color = Column("Color", Text)
	Size = Column("Size", Text)
	Materials = Column("Materials", Text)
	Compatibility = Column("Compatibility", Text)

metadata.create_all(engine)