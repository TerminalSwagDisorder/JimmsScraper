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
cpu = Table("cpu", metadata,
	Column("id", INTEGER, primary_key=True, autoincrement=True),
	Column("Name", TEXT),
	Column("Manufacturer", TEXT),
	Column("Core Count", TEXT),
	Column("Performance Core Clock", TEXT),
	Column("Performance Boost Clock", TEXT),
	Column("TDP", TEXT),
	Column("Integrated Graphics", TEXT),
	Column("L3 Cache", TEXT),
	Column("Simultaneous Multithreading", TEXT),
	Column("Includes CPU Cooler", TEXT),
	Column("Socket", TEXT),
	Column("Price", TEXT),
	Column("Url", TEXT)
)
gpu = Table("gpu", metadata,
	Column("id", INTEGER, primary_key=True, autoincrement=True),
	Column("Name", TEXT),
	Column("Manufacturer", TEXT),
	Column("Chipset", TEXT),
	Column("Memory", TEXT),
	Column("Memory Type", TEXT),
	Column("Core Clock", TEXT),
	Column("Boost Clock", TEXT),
	Column("Effective Memory Clock", TEXT),
	Column("Interface", TEXT),
	Column("Color", TEXT),
	Column("Length", TEXT),
	Column("TDP", TEXT),
	Column("Expansion Slot Width", TEXT),
	Column("Cooling", TEXT),
	Column("Price", TEXT),
	Column("Url", TEXT)
)
cooler = Table("cpu cooler", metadata,
	Column("id", INTEGER, primary_key=True, autoincrement=True),
	Column("Name", TEXT),
	Column("Manufacturer", TEXT),
	Column("Fan RPM", TEXT),
	Column("Noise Level", TEXT),
	Column("Color", TEXT),
	Column("Height", TEXT),
	Column("Water Cooled", TEXT),
	Column("Fanless", TEXT),
	Column("Price", TEXT),
	Column("Url", TEXT)
)
motherboard = Table("motherboard", metadata,
	Column("id", INTEGER, primary_key=True, autoincrement=True),
	Column("Name", TEXT),
	Column("Manufacturer", TEXT),
	Column("Socket / CPU", TEXT),
	Column("Form Factor", TEXT),
	Column("Chipset", TEXT),
	Column("Memory Max", TEXT),
	Column("Memory Type", TEXT),
	Column("Memory Slots", TEXT),
	Column("Color", TEXT),
	Column("PCIe x16 Slots", TEXT),
	Column("PCIe x8 Slots", TEXT),
	Column("PCIe x4 Slots", TEXT),
	Column("PCIe x1 Slots", TEXT),
	Column("M.2 Slots", TEXT),
	Column("SATA 6.0 Gb/s", TEXT),
	Column("Onboard Ethernet", TEXT),
	Column("USB 2.0 Headers", TEXT),
	Column("USB 3.2 Gen 1 Headers", TEXT),
	Column("USB 3.2 Gen 2 Headers", TEXT),
	Column("USB 3.2 Gen 2x2 Headers", TEXT),
	Column("Wireless Networking", TEXT),
	Column("RAID Support", TEXT),
	Column("Price", TEXT),
	Column("Url", TEXT)
)
memory = Table("memory", metadata,
	Column("id", INTEGER, primary_key=True, autoincrement=True),
	Column("Name", TEXT),
	Column("Manufacturer", TEXT),
	Column("Form Factor", TEXT),
	Column("Modules", TEXT),
	Column("Color", TEXT),
	Column("CAS Latency", TEXT),
	Column("Voltage", TEXT),
	Column("ECC / Registered", TEXT),
	Column("Heat Spreader", TEXT),
	Column("Price", TEXT),
	Column("Url", TEXT)
)
storage = Table("storage", metadata,
	Column("id", INTEGER, primary_key=True, autoincrement=True),
	Column("Name", TEXT),
	Column("Manufacturer", TEXT),
	Column("Capacity", TEXT),
	Column("Type", TEXT),
	Column("Cache", TEXT),
	Column("Form Factor", TEXT),
	Column("Interface", TEXT),
	Column("NVME", TEXT),
	Column("Price", TEXT),
	Column("Url", TEXT)
)
psu = Table("psu", metadata,
	Column("id", INTEGER, primary_key=True, autoincrement=True),
	Column("Name", TEXT),
	Column("Manufacturer", TEXT),
	Column("Form Factor", TEXT),
	Column("Efficiency Rating", TEXT),
	Column("Wattage", TEXT),
	Column("Length", TEXT),
	Column("Modular", TEXT),
	Column("Color", TEXT),
	Column("Type", TEXT),
	Column("Fanless", TEXT),
	Column("ATX Connectors", TEXT),
	Column("EPS Connectors", TEXT),
	Column("PCIe 12-Pin Connectors", TEXT),
	Column("PCIe 8-Pin Connectors", TEXT),
	Column("PCIe 6+2-Pin Connectors", TEXT),
	Column("PCIe 6-Pin Connectors", TEXT),
	Column("SATA Connectors", TEXT),
	Column("Molex 4-Pin Connectors", TEXT),
	Column("Price", TEXT),
	Column("Url", TEXT)
)
case = Table("case", metadata,
	Column("id", INTEGER, primary_key=True, autoincrement=True),
	Column("Name", TEXT),
	Column("Manufacturer", TEXT),
	Column("Type", TEXT),
	Column("Color", TEXT),
	Column("Power Supply", TEXT),
	Column("Side Panel Window", TEXT),
	Column("Power Supply Shroud", TEXT),
	Column("Motherboard Form Factor", TEXT),
	Column("Maximum Video Card Length", TEXT),
	Column("Volume", TEXT),
	Column("Dimensions", TEXT),
	Column("Price", TEXT),
	Column("Url", TEXT)
)
metadata.create_all(engine)