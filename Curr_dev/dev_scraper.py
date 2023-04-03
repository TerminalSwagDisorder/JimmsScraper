# File name: dev_scraper.py
# Auth: Benjamin Willför/TerminalSwagDisorder & Sami Wazni
# Desc: File currently in development containing code for a scraper for jimms.com

import database
from pypartpicker import Scraper
from time import sleep as sleep

# Jimms's cookie
def cookie():
	cookie = "xcsrftoken=EFfIzI0iN72Gcs1uNUQg0tF7i5q8GvhZLWX8i5CVGAe7OOAeu9q6uMWVTJmDPb6F; xgdpr-consent=allow; cf_chl_2=a48bb399a3e3c93; cf_clearance=DKR.1AeYMvNSSTcncxq7dvTrD36IwOqsN4UT89h.IGw-1677567188-0-250"
	user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"

	pcpartpicker = Scraper(headers={ "cookie": cookie, "user-agent": user_agent })

	print("starting extraction\n")

def main():
	# Add anything you want to find from https://fi.pcpartpicker.com/search/
	# Primary part categories are "processsor", "video card", "cpu cooler", "motherboard", "memory", "internal hard drive", "solid state drive", "power supply", "case"
	searchTerms = ["video card gtx", "video card rtx", "video card radeon", "processor amd ryzen", "processor intel celeron", "processor intel pentium", "processor intel core i3", "processor intel core i5", "processor intel core i7", "processor intel core i9", "cpu cooler", "motherboard", "memory ddr4", "memory ddr5", "memory ddr3", "internal hard drive",  "solid state drive 2.5", "solid state drive m.2", "power supply certified", "atx case", "itx case", "htpc case"]

def check_record_exists(session, main_parts, name):
	for single_part in main_parts:
		if single_part == "cpu":
			query = session.query(database.cpu).filter(database.cpu.c.Name == name).first()
			if query:
				return True
		
		elif single_part == "gpu":
			query = session.query(database.gpu).filter(database.gpu.c.Name == name).first()
			if query:
				return True
			
		elif single_part == "cooler":
			query = session.query(database.cooler).filter(database.cooler.c.Name == name).first()
			if query:
				return True
			
		elif single_part == "motherboard":
			query = session.query(database.motherboard).filter(database.motherboard.c.Name == name).first()
			if query:
				return True
			
		elif single_part == "memory":
			query = session.query(database.memory).filter(database.memory.c.Name == name).first()
			if query:
				return True
			
		elif single_part == "storage":
			query = session.query(database.storage).filter(database.storage.c.Name == name).first()
			if query:
				return True
			
		elif single_part == "psu":
			query = session.query(database.psu).filter(database.psu.c.Name == name).first()
			if query:
				return True
			
		elif single_part == "case":
			query = session.query(database.case).filter(database.case.c.Name == name).first()
			if query:
				return True
			
main()