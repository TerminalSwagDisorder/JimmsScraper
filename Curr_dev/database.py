# File name: database.py
# Auth: Benjamin Willför/TerminalSwagDisorder & Sami Wazni
# Desc: File currently in development containing code for creating a database

from pathlib import Path
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import ColumnClause
from sqlalchemy.sql import table, column, select, update, insert, delete, text
from sqlalchemy.ext.declarative import declarative_base


def create_database():
	# Create database folder if it does not exist
	fPath = Path(__file__).resolve()
	dPath = fPath.parent
	finPath = dPath.joinpath("database")

	if not finPath.exists():
		finPath.mkdir()

	engine = create_engine("sqlite:///" + str(finPath.joinpath("pcbuildwebsite_db.db")), echo=True, pool_pre_ping=True)
	Session = sessionmaker(bind=engine)
	session = Session()

    # Define metadata information
	metadata = MetaData()

	return engine, session, metadata

engine, session, metadata = create_database()

Base = declarative_base()

# Create tables in database	 
class UniversalComponents(Base):
	__abstract__ = True
	ID = Column("ID", INTEGER, primary_key = True, autoincrement = True)
	Price = Column("Price", TEXT)
	Url = Column("Url", TEXT)
	Name = Column("Name", TEXT)
	Manufacturer = Column("Manufacturer", TEXT)

	__tablename__ = "universal_components"
	__mapper_args__ = {
		"polymorphic_identity": "universal_components",
		"concrete": True
	}

class CPU(UniversalComponents):
	__tablename__ = "cpu"
	__table_args__ = (
		Column("Core Count", TEXT),
		Column("Thread Count", TEXT),
		Column("Base Clock", TEXT),
		Column("Boost Clock", TEXT),
		Column("L3 Cache", TEXT),
		Column("Socket", TEXT),
		Column("PCie Version", TEXT),
		Column("Cpu Cooler", TEXT),
		Column("TDP", TEXT),
		Column("Integrated GPU", TEXT)
	)

class GPU(UniversalComponents):
	__tablename__ = "gpu"

	__table_args__ = (
		Column("Cores", TEXT),
		Column("Memory", TEXT),
		Column("Core Clock", TEXT),
		Column("Interface", TEXT),
		Column("Size", TEXT),
		Column("TDP", TEXT),
	)

class Cooler(UniversalComponents):
	__tablename__ = "cpu cooler"

	__table_args__ = (
		Column("Color", TEXT),
		Column("Fan RPM", TEXT),
		Column("Noise Level", TEXT),
		Column("Height", TEXT)
	)

class Motherboard(UniversalComponents):
	__tablename__ = "motherboard"

	__table_args__ = (
		Column("Form factor", TEXT),
		Column("Mermory Type", TEXT),
		Column("Memory Slots", TEXT)
	)

class Memory(UniversalComponents):
	__tablename__ = "memory"

	__table_args__ = (
		Column("Modules", TEXT),
		Column("Color", TEXT)
	)

class Storage(UniversalComponents):
	__tablename__ = "storage"

	__table_args__ = (
		Column("Capacity", TEXT),
		Column("Form factor", TEXT),
		Column("Interface", TEXT),
		Column("Cache", TEXT),
		Column("Flash", TEXT),
		Column("TBW", TEXT)
	)

class PSU(UniversalComponents):
	__tablename__ = "psu"

	__table_args__ = (
		Column("is_ATX12V", TEXT),
		Column("Dimensions", TEXT)
	)

class Case(UniversalComponents):
	__tablename__ = "case"

	__table_args__ = (
		Column("Color", TEXT),
		Column("Size", TEXT),
		Column("Materials", TEXT),
		Column("Compatibility", TEXT)

	)

Base.metadata.create_all(engine)