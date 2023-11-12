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

Base = declarative_base()

# Create tables in database	 
class UniversalComponents(Base):
	__abstract__ = True
	ID = Column("ID", INTEGER, primary_key = True, autoincrement = True)
	Url = Column("Url", TEXT)
	Price = Column("Price", TEXT)
	Name = Column("Name", TEXT)
	Manufacturer = Column("Manufacturer", TEXT)
	Image = Column("Image", TEXT)
	Image_Url = Column("Image_Url", TEXT)

	__tablename__ = "universal_components"
	__mapper_args__ = {
		"polymorphic_identity": "universal_components",
		"concrete": True
	}

class CPU(UniversalComponents):
	__tablename__ = "cpu"
	__table_args__ = (
		Column("Core_Count", TEXT),
		Column("Thread_Count", TEXT),
		Column("Base_Clock", TEXT),
		Column("Cache", TEXT),
		Column("Socket", TEXT),
		Column("Cpu_Cooler", TEXT),
		Column("TDP", TEXT),
		Column("Integrated_GPU", TEXT)
	)

class GPU(UniversalComponents):
	__tablename__ = "gpu"

	__table_args__ = (
		Column("Cores", TEXT),
		Column("Core_Clock", TEXT),
		Column("Memory", TEXT),
		Column("Interface", TEXT),
		Column("Dimensions", TEXT),
		Column("TDP", TEXT)
	)

class Cooler(UniversalComponents):
	__tablename__ = "cpu_cooler"

	__table_args__ = (
		Column("Compatibility", TEXT),
		Column("Cooling_Potential", TEXT),
		Column("Fan_RPM", TEXT),
		Column("Noise_Level", TEXT),
		Column("Dimensions", TEXT)
	)

class Motherboard(UniversalComponents):
	__tablename__ = "motherboard"

	__table_args__ = (
		Column("Chipset", TEXT),
		Column("Form_Factor", TEXT),
		Column("Memory_Compatibility", TEXT)
	)

class Memory(UniversalComponents):
	__tablename__ = "memory"

	__table_args__ = (
		Column("Type", TEXT),
		Column("Amount", TEXT),
		Column("Speed", TEXT),
		Column("Latency", TEXT)
	)

class Storage(UniversalComponents):
	__tablename__ = "storage"

	__table_args__ = (
		Column("Capacity", TEXT),
		Column("Form_Factor", TEXT),
		Column("Interface", TEXT),
		Column("Cache", TEXT),
		Column("Flash", TEXT),
		Column("TBW", TEXT)
	)

class PSU(UniversalComponents):
	__tablename__ = "psu"

	__table_args__ = (
		Column("Is_ATX12V", TEXT),
		Column("Efficiency", TEXT),
		Column("Modular", TEXT),
		Column("Dimensions", TEXT)
	)

class Chassis(UniversalComponents):
	__tablename__ = "chassis"

	__table_args__ = (
		Column("Chassis_type", TEXT),
		Column("Dimensions", TEXT),
		Column("Color", TEXT),
		Column("Compatibility", TEXT)

	)
