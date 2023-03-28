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


Base = declarative_base()
# Create table in database	 
class UniversalComponents(Base):
	__abstract__ = True
	ID = Column(INTEGER, primary_key=True, autoincrement=True)
	Name = Column(TEXT)
	Manufacturer = Column(TEXT)
	Price = Column(TEXT)
	Url = Column(TEXT)

	__tablename__ = 'universal_components'
	__mapper_args__ = {
		'polymorphic_identity': 'universal_components',
		'concrete': True
	}

class CPU(UniversalComponents):
	__tablename__ = 'cpu'

	Core_Count = Column("Core Count", TEXT)
	Thread_Count = Column("Thread Count", TEXT)
	Performance_Base_Clock = Column("Base Clock", TEXT)
	Performance_Boost_Clock = Column("Boost Clock", TEXT)
	L3_Cache = Column("L3 Cache", TEXT)
	Socket = Column("Socket", TEXT)
	PCIe_Ver = Column("PCie Version", TEXT)
	Includes_CPU_Cooler = Column("Cpu Cooler", TEXT)
	TDP = Column("TDP", TEXT)
	Integrated_Graphics = Column("Integrated GPU", TEXT)

class PSU(UniversalComponents):
	__tablename__ = 'psu'
	is_ATX12V = Column("is_ATX12V", TEXT)
	Dimensions = Column("Dimensions", TEXT)

class Case(UniversalComponents):
	__tablename__ = 'case'
	Color = Column("Color", TEXT)
	Size = Column("Size", TEXT)
	Materials = Column("Materials", TEXT)
	Compatibility = Column("Compatibility", TEXT)

Base.metadata.create_all(engine)

