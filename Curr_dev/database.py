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
	__table_args__ = (
        Column('Core Count', TEXT),
        Column('Thread Count', TEXT),
        Column('Base Clock', TEXT),
        Column('Boost Clock', TEXT),
        Column('L3 Cache', TEXT),
        Column('Socket', TEXT),
        Column('PCie Version', TEXT),
        Column('Cpu Cooler', TEXT),
        Column('TDP', TEXT),
        Column('Integrated GPU', TEXT)
	)

class GPU(UniversalComponents):
	__tablename__ = 'gpu'
	__table_args__ = (
        Column("Color", TEXT),
		Column("Memory", TEXT),
		Column("Memory Type", TEXT),
		Column("Core Clock", TEXT),
		Column("Boost Clock", TEXT),
		Column("Effective Memory Clock", TEXT),
		Column("Interface", TEXT),
		Column("TDP", TEXT),
		Column("Cooling", TEXT)
	)	

class Cooler(UniversalComponents):
	__tablename__ = 'cpu cooler'
	__table_args__ = (
        Column("Color", TEXT),
		Column("Fan RPM", TEXT),
		Column("Noise Level", TEXT),
		Column("Height", TEXT)
	)	

class Motherboard(UniversalComponents):
	__tablename__ = 'motherboard'
	__table_args__ = (
        Column("Color", TEXT),
		Column("Mermory Type", TEXT),
		Column("Memory Max", TEXT),
		Column("Memory Slots", TEXT)
	)	

class Memory(UniversalComponents):
	__tablename__ = 'memory'
	__table_args__ = (
        Column("Modules", TEXT),
		Column("Color", TEXT)
	)	

class Storage(UniversalComponents):
	__tablename__ = 'storage'
	__table_args__ = (
		Column("Capacity", TEXT),
		Column("Type", TEXT),
		Column("Interface", TEXT)
	)	

class PSU(UniversalComponents):
	__tablename__ = 'psu'
	__table_args__ = (
		Column("is_ATX12V", TEXT),
		Column("Dimensions", TEXT)
	)	

class Case(UniversalComponents):
	__tablename__ = 'case'
	__table_args__ = (
		Column("Color", TEXT),
		Column("Size", TEXT),
		Column("Materials", TEXT),
		Column("Compatibility", TEXT)
	)	
	
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
