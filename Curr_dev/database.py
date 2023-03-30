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

class GPU(UniversalComponents):
	__tablename__ = 'gpu'

	Color = Column("Color", TEXT)
	Memory = Column("Memory", TEXT)
	Memory_Typ = Column("Memory Type", TEXT)
	Core_Clock = Column("Core Clock", TEXT)
	Boost_Clock = Column("Boost Clock", TEXT)
	Effective = Column("Effective Memory Clock", TEXT)
	Interface = Column("Interface", TEXT)
	TDP = Column("TDP", TEXT)
	Cooling = Column("Cooling", TEXT)

class Cooler(UniversalComponents):
	__tablename__ = 'cpu cooler'
	
	Color = Column("Color", TEXT)
	Fan_RPM = Column("Fan RPM", TEXT)
	Noise_Level = Column("Noise Level", TEXT)
	Height = Column("Height", TEXT)

class Motherboard(UniversalComponents):
	__tablename__ = 'motherboard'

	Color = Column("Color", TEXT)
	Mermory_Type = Column("Mermory Type", TEXT)
	Memory_Max = Column("Memory Max", TEXT)
	Memory_Slots = Column("Memory Slots", TEXT)

class Memory(UniversalComponents):
	__tablename__ = 'memory'

	Modules = Column("Modules", TEXT)
	Color = Column("Color", TEXT)

class Storage(UniversalComponents):
	__tablename__ = 'storage'

	Capacity = Column("Capacity", TEXT)
	Type = Column("Type", TEXT)
	Interface = Column("Interface", TEXT)

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


# For specifying a order use __table_args__ 
'''
class CPU(UniversalComponents):
    __tablename__ = 'cpu'
    __table_args__ = (
        Column('ID', INTEGER, primary_key=True, autoincrement=True),
        Column('Name', TEXT),
        Column('Core Count', TEXT),
        Column('Thread Count', TEXT),
        Column('Base Clock', TEXT),
        Column('Boost Clock', TEXT),
        Column('L3 Cache', TEXT),
        Column('Socket', TEXT),
        Column('PCie Version', TEXT),
        Column('Cpu Cooler', TEXT),
        Column('TDP', TEXT),
        Column('Integrated GPU', TEXT),
        Column('Price', TEXT),
        Column('Url', TEXT)
    )
'''
