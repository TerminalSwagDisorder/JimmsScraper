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

# Create table in database	   
metadata.create_all(engine)



Base = declarative_base()

class CPU(Base):
	__tablename__ = 'cpu',

	Core_Count = Column("Core Count", text),
	Thread_Count = Column("Thread Count", text),
	Performance_Base_Clock = Column("Base Clock", text),
	Performance_Boost_Clock = Column("Boost Clock", text),
	L3_Cache = Column("L3 Cache", text),
	Socket = Column("Socket", text),
	PCIe_Ver = Column("PCie Version", text),
	Includes_CPU_Cooler = Column("Cpu Cooler", text),
	TDP = Column("TDP", text),
	Integrated_Graphics = Column("Integrated GPU", text)

Base.metadata.create_all(engine)
