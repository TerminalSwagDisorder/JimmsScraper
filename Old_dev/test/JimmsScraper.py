from pypartpicker import Scraper
from time import sleep as sleep
import os
import sqlite3
import itertools
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import ColumnClause
from sqlalchemy.sql import table, column, select, update, insert, delete, text
from sqlalchemy.ext.declarative import *
from sqlalchemy import create_engine



fPath = os.path.abspath(os.path.realpath(__file__))
dPath = os.path.dirname(fPath)
finPath = dPath + "\\database"

#Create database folder if it does not exist
if not os.path.exists(finPath):
	os.makedirs(finPath)

engine = create_engine("sqlite:///" + finPath + "\\pcbuildwebsite_db.db", echo=True, pool_pre_ping=True)
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
session = Session(bind=engine)

#Define metadata information
metadata = MetaData(bind=engine)

#Create table in database	   
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
metadata.create_all(engine)

cookie = "xcsrftoken=EFfIzI0iN72Gcs1uNUQg0tF7i5q8GvhZLWX8i5CVGAe7OOAeu9q6uMWVTJmDPb6F; cf_chl_2=d1b03c8d4dee956; cf_clearance=MlrWGWxW7hi0XGJw9vIDUSqUdzrRbit.gfy_WZlNzGE-1676034980-0-250; xgdpr-consent=allow"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
accept_encoding = "gzip, deflate, br"
accept_language = "en-GB,en;q=0.9,en-US;q=0.8,sv;q=0.7,fi;q=0.6"
referer = "https://pcpartpicker.com/?__cf_chl_tk=BRzM_cKd1nhA..cUaKzadxlmrR.AlaAt9YTptZin6TQ-1676034967-0-gaNycGzNC9A"
origin = "https://pcpartpicker.com"

pcpartpicker = Scraper(headers={ "cookie": cookie, "user-agent": user_agent })
print("starting extraction\n")

searchTerms = ["processor amd ryzen"]

def check_record_exists(session, cpu, name):
    query = session.query(cpu).filter(cpu.c.Name == name).first()
    return True if query else False

#Extract data and insert to database
for partcategory in searchTerms:
	print("\nstarting", partcategory)
	parts = pcpartpicker.part_search(partcategory, limit=500, region="fi")
	
	for part in parts:
		print("debug 1")
		if not part.price is None:
			validpart = pcpartpicker.fetch_product(part.url)

			print("debug 2")
			sleep(3)
			partname = {
				"Name" : part.name,
			}
			partprice = {
				"Price" : part.price,
			}
			parturl = {
				"Url" : part.url,
			}
			#Convert specs into only dict
			vs = [{new_k : new_val[r] for new_k, new_val in validpart.specs.items()} for r in range(1)]
			specsdict = {
				
			}
			
			for key, value in vs[0].items():
				specsdict[key] = value
			
			#Delete unecessary dict columns	
			delcol = ["Efficiency L1 Cache", "Efficiency L2 Cache", "Part #", "Series", "Microarchitecture", "Core Family", "Maximum Supported Memory", "ECC Support", "Packaging", "Performance L1 Cache", "Performance L2 Cache", "Lithography", "Frame Sync", "Efficiency", "Includes Cooler"]
						
			for column in delcol:
				try:
					specsdict.pop(column)
				except:
					continue
					
			# Update if record exists, insert otherwise
			if check_record_exists(session, cpu, part.name):
				print("Product already exists in database, updating existing data")
				session.query(cpu).filter(cpu.c.Name == part.name).update(
					{
						"Manufacturer": specsdict.get("Manufacturer", None),
						"Core Count": specsdict.get("Core Count", None),
						"Performance Core Clock": specsdict.get("Performance Core Clock", None),
						"Performance Boost Clock": specsdict.get("Performance Boost Clock", None),
						"TDP": specsdict.get("TDP", None),
						"Integrated Graphics": specsdict.get("Integrated Graphics", None),
						"L3 Cache": specsdict.get("L3 Cache", None),
						"Simultaneous Multithreading": specsdict.get("Simultaneous Multithreading", None),
						"Includes CPU Cooler": specsdict.get("Includes CPU Cooler", None),
						"Socket": specsdict.get("Socket", None),
						"Price": partprice["Price"],
						"Url": parturl["Url"],
					}
				)
			else:
				i = insert(cpu)
				i = i.values(partname)
				i = i.values(specsdict) 
				i = i.values(partprice)  
				i = i.values(parturl)
				session.execute(i)
		session.commit()

			
		sleep(8)