# File name: dev_scraper.py
# Auth: Benjamin Willför/TerminalSwagDisorder & Sami Wazni
# Desc: File currently in development containing code for a scraper for jimms.com

import database
import requests
import time
import threading
from pathlib import Path
from bs4 import BeautifulSoup
from time import sleep as sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from pprint import pprint as pprint
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import table, column, select, update, insert, delete, text
from sqlalchemy import create_engine


def main():
	# Urls for jimms
	base_url = "https://www.jimms.fi"
	product_url = "/fi/Product/Show/"
	component_url = ["/fi/Product/List/000-00R/komponentit--prosessorit"]
	
	component_url2 = ["/fi/Product/List/000-00K/komponentit--kiintolevyt-ssd-levyt", "/fi/Product/List/000-00H/komponentit--emolevyt", "/fi/Product/List/000-00J/komponentit--kotelot", "/fi/Product/List/000-00M/komponentit--lisakortit", "/fi/Product/List/000-00N/komponentit--muistit", "/fi/Product/List/000-00P/komponentit--naytonohjaimet", "/fi/Product/List/000-00R/komponentit--prosessorit", "/fi/Product/List/000-00U/komponentit--virtalahteet", "/fi/Product/List/000-104/jaahdytys-ja-erikoistuotteet--jaahdytyssiilit"]

	# Do a speedtest to jimms
	speed_passed = speedtest(base_url)

	if not speed_passed:
		speed_input = input(f"Speedtest either failed or was low, do you still want to continue? (Y/yes) \n")

		if speed_input.upper() in ["Y", "YES"]:
			print("Continuing...")
		else:
			print("Stopping...")
			return

	engine, session, metadata, CPU, GPU, Cooler, Motherboard, Memory, Storage, PSU, Case = database_connection()

	index_pages_dict = get_subpages(base_url, component_url)
	all_product_links = get_urls(base_url, index_pages_dict)

	sleep(2)
	data_scraper(base_url, all_product_links, engine, session, metadata, CPU, GPU, Cooler, Motherboard, Memory, Storage, PSU, Case)
	session.close()
	print("\n\n")
	print("Scraping completed")

def check_download_speed(url):
	# Get the values for the download speed
	try:
		start_time = time.time()
		response = requests.get(url)
		response.raise_for_status()
		end_time = time.time()
		download_time = end_time - start_time
		download_speed = len(response.content) / download_time / 1024
		return download_speed

	except (requests.exceptions.RequestException, requests.exceptions.HTTPError):
		return None

def speedtest(base_url):
	speed_list = []

	# Minimum acceptable download speed
	min_speed = 500

	# Check the average of 5 speedtests against minimum speed
	while len(speed_list) < 5:
		speed = check_download_speed(base_url)
		speed_list.append(speed)

	avg_speed = sum(speed_list) / len(speed_list) if None not in speed_list else None

	if avg_speed is not None and avg_speed > min_speed:
		print(f"\nDownload speed to '{base_url}' is good ({avg_speed:.2f} kb/s)\n")
		speed_passed = True
	elif avg_speed is not None and avg_speed < min_speed:
		print(f"\nWARNING: Download speed to '{base_url}' is low ({avg_speed:.2f} kb/s)\n")
		speed_passed = False
	else:
		print(f"\nERROR: Failed to check download speed to '{base_url}'\n")
		speed_passed = False

	return speed_passed

def database_connection():
	# Location of current directory
	fPath = Path(__file__).resolve()
	dPath = fPath.parent
	finPath = dPath.joinpath("database")

	# Create a connection to the database
	engine = create_engine("sqlite:///" + str(finPath.joinpath("pcbuildwebsite_db.db")), echo=True, pool_pre_ping=True)
	Session = sessionmaker(bind = engine)
	session = Session()
	metadata = MetaData()

	CPU = database.CPU.__table__

	GPU = database.GPU.__table__

	Cooler = database.Cooler.__table__

	Motherboard = database.Motherboard.__table__

	Memory = database.Memory.__table__

	Storage = database.Storage.__table__

	PSU = database.PSU.__table__

	Case = database.Case.__table__

	return engine, session, metadata, CPU, GPU, Cooler, Motherboard, Memory, Storage, PSU, Case



def get_meta(item_soup, metasearch):
		meta_location = item_soup.find("meta", metasearch)
		metadata = meta_location["content"]

		return metadata

def strong_search(results_item, strong_desc):
	# Get strong item with string from description
	try:
		strong_location = results_item.select_one(f"strong:-soup-contains('{strong_desc}')")
		strong_list = []

		if strong_location is not None:
			strong_data = strong_location.find_next_siblings(string = True)
			for item in strong_data:
				if item != ":" and item is not None and item not in strong_list:
					strong_list.append(item)
			strong_list = strong_list[0]
		else:
			strong_list = None

	except:
		strong_list = None

	return strong_list


def trim_list(item_list):
	for i, item in enumerate(item_list):
		if item and item != None:
			
			# Trim each item by removing the colon and everything it
			data = item.split(":", 1)
			if len(data) > 1:
				item_list[i] = data[1].strip().capitalize()
			else:
				item_list[i] = item.strip().capitalize()
			
			# Translate kyllä and ei
			if item_list[i].upper() == "KYLLÄ" and len(item_list[i]) < 7:
				item_list[i] = "Yes"
			elif item_list[i].upper() == "EI" and len(item_list[i]) < 4:
				item_list[i] = "No"
	return item_list


def process_subpages(base_url, index_pages_dict, item, lock):
	# Create selenium instance
	driver_path = "./chromedriver_win32/chromedriver.exe"
	driver = webdriver.Chrome(executable_path = driver_path)
	
	# Get subpages for all components
	try: 
		parameter = "?p="
		page_index = [1]

		print("Getting all pages for", item)

		# Go to page using Selenium
		driver.get(base_url + item + "?p=1")
		wait = WebDriverWait(driver, 10)
		button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@data-bind='click: moveToLastPage']")))
		driver.execute_script("arguments[0].click();", button)
		sleep(2)

		# Get the url
		last_page_url = driver.current_url
		last_page_number = int(last_page_url.split("=")[-1])
		page_index.append(last_page_number)

		# Add subpage numbers to page_index
		page_nums = range(page_index[0] + 1, page_index[1])
		for num in page_nums:
			lock.acquire()
			page_index.append(num)
			lock.release()
			page_index.sort()

		# Create a new list with added parameter
		pages_with_param = [parameter + str(page) for page in page_index]

		# Create a list/dictionary with all subpages
		index_pages_dict[item] = [parameter + str(page) for page in page_index]

		sleep(2)
	except Exception as e:
		print(f"Error while processing {item}: {e}")	
	finally:
		driver.close()
		driver.quit()

def get_subpages(base_url, component_url):

	
	index_pages_dict = {}

	lock = threading.Lock()
	threads = []

	for item in component_url:
		# Speed the process up
		thread = threading.Thread(target=process_subpages, args=(base_url, index_pages_dict, item, lock))
		thread.start()
		threads.append(thread)

	for thread in threads:
		thread.join()


	print("All subpages scraped")
	return index_pages_dict

def process_url(curr_url, all_product_links, lock):
	try:
		# Parse and iterate through the html using bs4
		product_list_page = requests.get(curr_url)
		next_soup = BeautifulSoup(product_list_page.content, "html.parser")
		page_content = next_soup.find("div", class_="product-list-wrapper")
		product_name = page_content.find_all("h5", class_="product-box-name")

		# Get the actual link for each item
		for item in product_name:
			if "Tarjous" not in item.text and "Bundle" not in item.text and "Outlet" not in item.text:
				product_link = item.find("a", href=True)
				get_link = product_link.get("href")
				
				lock.acquire()
				all_product_links.append(get_link)
				lock.release()
				
				sleep(0.2)
			else:
				print("Skipped reduced or bundled item")
	except Exception as e:
		print(f"Error while processing {curr_url}: {e}")
	else:
		print(f"{len(all_product_links)} links found")	


def get_urls(base_url, index_pages_dict):
	all_product_links = []

	lock = threading.Lock()
	threads = []

	# Get links for all the products
	for key, value in index_pages_dict.items():
		for index in value:
			curr_url = base_url + key + index

			# Speed the process up
			thread = threading.Thread(target=process_url, args=(curr_url, all_product_links, lock))
			thread.start()
			threads.append(thread)

	for thread in threads:
		thread.join()
	
	print(f"{len(all_product_links)} links found\n")
	sleep(2)
	return all_product_links


def data_scraper(base_url, all_product_links, engine, session, metadata, CPU, GPU, Cooler, Motherboard, Memory, Storage, PSU, Case):

	for product in all_product_links:
		curr_link = base_url + product
		item_page = requests.get(curr_link, allow_redirects=True)
		item_soup = BeautifulSoup(item_page.content, "html.parser")

		# Get product category
		category_link = item_soup.find_all("a", class_="link-secondary")[2]
		get_category = category_link.get("href")


		# Testing getting the data with metadata
		m_manufacturer = get_meta(item_soup, {"property": "product:brand"})
		m_price = get_meta(item_soup, {"property": "product:price:amount"})
		m_desc = get_meta(item_soup, {"property": "og:description"})

		# Get the short description 
		short_desc = item_soup.find(class_="jim-product-cta-box-shortdescription")
		if short_desc:
			short_desc = short_desc.get_text().strip("\xa0-").strip().split(", ")

		# Get the name
		name_location = item_soup.find("h1")
		name_item = name_location.find_all("span", itemprop="name")

		name_list = []
		for name in name_item:
			for trim in name.stripped_strings:
				if trim and trim not in name_list:
					name_list.append(trim)

		trimmed_name = name_list[1].split(",", 1)
		trimmed_name = trimmed_name[0].strip().capitalize()


		# Get the description
		results_item = item_soup.find("div", itemprop="description")


		# Get all of the description data and trim it
		print("Current page:", curr_link)
		desc_data = results_item.select_one("strong:-soup-contains('Tekniset tiedot')")
		#desc_data = results_item.select_one(":contains('Tekniset tiedot')")
		if desc_data is not None:
			desc_list = []

			trimmed_data_p = results_item.contents
			print("trimmed_data_p")

			for sibling in trimmed_data_p:
				if sibling is not None and sibling != "":

					# In case there is a ul item, get it separately
					if sibling.name == "ul":

						ul_title = sibling.find_previous_sibling()
						ul_title = ul_title.get_text("\n").strip("\xa0-").strip().splitlines()
						while True:
							if ul_title[-1] == ":" or ul_title[-1] == "":
								del ul_title[-1]
							else:
								ul_title = ul_title[-1]
								break

						if ":" not in ul_title:
							ul_title = ul_title + ":"


						sibling_trim = sibling.get_text().strip("\xa0-").strip().splitlines()

						if not any(":" in skip for skip in sibling_trim):
							sibling_trim = "; ".join(sibling_trim)

						if isinstance(sibling_trim, list):
							for list_item in sibling_trim:
								desc_list.append(list_item)
						else:
							ul_item = f"{ul_title} {sibling_trim}"
							desc_list.append(ul_item)

						# Delete unnecessary list items
						try:
							index = desc_list.index(ul_title)
							del desc_list[index]
						except ValueError:
							try:
								ul_title = ul_title.rstrip(":").rstrip()
								index = desc_list.index(ul_title)
								del desc_list[index]
							except:
								print("Something went wrong")


					else:
						# If the item is not a ul item
						sibling_trim = sibling.get_text("\n")
						tt_trim = sibling_trim.strip("\xa0-").strip()
						newline_trim = tt_trim.splitlines()
						if len(newline_trim) > 0 and newline_trim != "":
							for final_item in newline_trim:
									desc_list.append(final_item)

				desc_list = [x for x in desc_list if x != "" and x != ":"]
				# Remove everything before Tekniset tiedot
				if "Tekniset tiedot:" in desc_list:
					index = desc_list.index("Tekniset tiedot:")
					desc_list = desc_list[index:]
				elif "Tekniset tiedot" in desc_list:
					index = desc_list.index("Tekniset tiedot")
					desc_list = desc_list[index:]

				# Format items better
				try:
					for i, item in enumerate(desc_list):
						if item.startswith(":"):
							desc_list[i] = desc_list[i-1] + desc_list[i]
							del desc_list[i-1]
						if item.endswith(":"):
							desc_list[i] = desc_list[i] + desc_list[i+1]
							del desc_list[i+1]
				except IndexError as e:
					print(f"Error: {e}")
				except:
					print("Undefined error")




		sleep(0.1)

		#pprint(name_list)
		#pprint(desc_list)


		# Use special searches in case of bad HTML formatting
		if "/fi/Product/List/000-00H" in get_category:
			chipset_list = strong_search(results_item, "Piirisarja")
			mobo_ff_list = strong_search(results_item, "Emolevyn tyyppi")
			mobo_memory_list = strong_search(results_item, "Muisti")

		# Initialize upcoming variables
		capacity = None
		form_factor = None
		interface = None
		cache = None
		flash = None
		tbw = None
		chipset = None
		form_factor = None
		memory_compatibility = None
		case_type = None
		dimensions = None
		color = None
		compatibility = None
		mem_type = None
		amount = None
		speed = None
		latency = None
		cores = None
		clock = None
		memory = None
		interface = None
		tdp = None
		core_count = None
		thread_count = None
		base_clock = None
		cpu_cache = None
		socket = None
		cpu_cooler = None
		tdp = None
		igpu = None
		atx12v = None
		efficiency = None
		modular = None
		compatibility = None
		cooling_potential = None
		fan_rpm = None
		noise_level = None


		# Depending on what category is active, sort the data to the respective variables
		for desc in desc_list:

			if "/fi/Product/List/000-00K" in get_category:
				part_type = "storage"

				if "SSD-LEVY" in trimmed_name.upper():
					trimmed_name = trimmed_name.upper().strip("SSD-LEVY").strip().capitalize()
				# Try this V	
				#if any(s in desc.upper() for s in ["KAPASITEETTI", "MUISTIN KOKO"]) and ":" in desc and desc.index(":") > desc.upper().index("KAPASITEETTI") and not desc.strip().endswith(":"):
				if any(s in desc.upper() for s in ["KAPASITEETTI", "MUISTIN KOKO"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if capacity is None:
						capacity = desc

				elif any(s in desc.upper() for s in ["FORM FACTOR:", "M.2 TYYPPI", "MUOTO"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if form_factor is None:
						form_factor = desc

				elif any(s in desc.upper() for s in ["VÄYLÄ", "LIITÄNTÄ", "LIITÄNNÄT"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if interface is None:
						interface = desc

				elif any(s in desc.upper() for s in ["CACHE", "DRAM", "PUSKURI"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if cache is None:
						if any(s in desc.upper() for s in ["CACHELESS", "DRAMLESS"]):
							cache = None
						else:
							cache = desc

				elif any(s in desc.upper() for s in ["MUISTITYYPPI", "TALLENNUSMUISTI", "FLASH", "NAND"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if flash is None:
						flash = desc

				elif any(s in desc.upper() for s in ["TBW", "KÄYTTÖKESTÄVYYS", "TOTAL BYTES WRITTEN"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if tbw is None:
						tbw = desc


			elif "/fi/Product/List/000-00H" in get_category:
				part_type = "mobo"

				if any(s in desc.upper() for s in ["PIIRISARJA"]) and ":" in desc.upper() and not desc.strip().endswith(":") or chipset_list is not None:
					if chipset_list is not None:
						chipset = chipset_list
					elif chipset is None:
						chipset = desc



				elif any(s in desc.upper() for s in ["TUOTTEEN TYYPPI", "EMOLEVYN TYYPPI"]) and ":" in desc.upper() and not desc.strip().endswith(":") or mobo_ff_list is not None:
					if mobo_ff_list is not None:
						form_factor = mobo_ff_list
					elif form_factor is None:
						form_factor = desc


				elif any(s in desc.upper() for s in ["DIMM"]) and ":" in desc.upper() and not desc.strip().endswith(":") or mobo_memory_list is not None:
					if mobo_memory_list is not None:
						memory_compatibility = mobo_memory_list
					elif memory_compatibility is None:
						memory_compatibility = desc



			elif "/fi/Product/List/000-00J" in get_category:
				part_type = "case"

				if any(s in desc.upper() for s in ["KOTELOTYYPPI"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if case_type is None:
						case_type = desc

				elif "MAKSIMIMITAT" not in desc.upper() and any(s in desc.upper() for s in ["MITAT", "KXLXS", "LXPXK"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if dimensions is None:
						dimensions = desc

				elif any(s in desc.upper() for s in ["VÄRI"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if color is None:
						color = desc

				elif any(s in desc.upper() for s in ["YHTEENSOPIVUUS"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if compatibility is None:
						compatibility = desc


			elif "/fi/Product/List/000-00N" in get_category:
				part_type = "ram"

				if any(s in desc.upper() for s in ["TYYPPI"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if mem_type is None:
						mem_type = desc

				elif any(s in desc.upper() for s in ["KAPASITEETTI"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if amount is None:
						amount = desc

				elif any(s in desc.upper() for s in ["NOPEUS"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if speed is None:
						speed = desc

				elif any(s in desc.upper() for s in ["LATENSSI"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if latency is None:
						latency = desc



			elif "/fi/Product/List/000-00P" in get_category:
				part_type = "gpu"

				if "NÄYTÖNOHJAIN" in trimmed_name.upper():
					trimmed_name = trimmed_name.upper().strip("NÄYTÖNOHJAIN").strip().rstrip("-").strip().lstrip("-").strip().capitalize()

				if any(s in desc.upper() for s in ["CUDA", "STREAM-PROSESSORIT"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if cores is None:
						cores = desc

				elif any(s in desc.upper() for s in ["BOOST", "KELLOTAAJUUS"]) and "MHZ" in desc.upper() and ":" in desc.upper() and not desc.strip().endswith(":"):
					if clock is None:
						clock = desc

				elif any(s in desc.upper() for s in ["MÄÄRÄ"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if memory is None:
						memory = desc

				elif any(s in desc.upper() for s in ["VÄYLÄ"]) and not "MUISTIVÄYLÄ" in desc.upper() and ":" in desc.upper() and not desc.strip().endswith(":"):
					if interface is None:
						interface = desc

				elif any(s in desc.upper() for s in ["MITAT", "PITUUS", "KXLXS", "LXPXK"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if dimensions is None:
						dimensions = desc

				elif any(s in desc.upper() for s in ["TDP", "VIRTALÄHTE"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if tdp is None:
						tdp = desc


			elif "/fi/Product/List/000-00R" in get_category:
				part_type = "cpu"

				if any(s in desc.upper() for s in ["YDINTEN MÄÄRÄ"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if core_count is None:
						core_count = desc

				elif any(s in desc.upper() for s in ["THREADIEN MÄÄRÄ", "SÄIKEIDEN MÄÄRÄ"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if thread_count is None:
						thread_count = desc

				elif any(s in desc.upper() for s in ["KELLOTAAJUUS", "BASE CLOCK"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if base_clock is None:
						base_clock = desc

				elif any(s in desc.upper() for s in ["VÄLIMUISTI", "L3"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if cpu_cache is None:
						cpu_cache = desc

				elif any(s in desc.upper() for s in ["KANTA", "YHTEENSOPIVUUS"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if socket is None:
						socket = desc

				elif any(s in desc.upper() for s in ["JÄÄHDYTYS", "YHTEENSOPIVUUS"]) and not "EI SIS" in desc.upper() and ":" in desc.upper() and not desc.strip().endswith(":"):
					if cpu_cooler is None:
						cpu_cooler = desc

				elif any(s in desc.upper() for s in ["TDP"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if tdp is None:
						tdp = desc

				elif any(s in desc.upper() for s in ["NÄYTÖNOHJAIN", "RADEON", "VEGA"]) and not "EI SIS" in desc.upper() and ":" in desc.upper() and not desc.strip().endswith(":"):
					if igpu is None:
						igpu = desc


			elif "/fi/Product/List/000-00U" in get_category:
				part_type = "psu"

				if any(s in desc.upper() for s in ["ATX12V", "ATX 12 V"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if atx12v is None:
						atx12v = "True"

				elif any(s in desc.upper() for s in ["80 PLUS", "HYÖTYSUHDE"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if efficiency is None:
						efficiency = desc

				elif any(s in desc.upper() for s in ["MODULAARINEN", "MODULAR", "MODULAARISUUS"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if modular is None:
						if "TÄYSIN" in desc.upper():
							modular = "Fully modular"
						elif "SEMI" in desc.upper():
							modular = "Semi modular"
						else:
							modular = desc

				elif any(s in desc.upper() for s in ["MITAT", "KXLXS", "LXPXK"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if dimensions is None:
						dimensions = desc



			elif "/fi/Product/List/000-104" in get_category:
				part_type = "cooler"

				if "PROSESSORIJÄÄHDYTIN" in trimmed_name.upper():
					trimmed_name = trimmed_name.upper().strip("PROSESSORIJÄÄHDYTIN").strip().rstrip("-").strip().lstrip("-").strip().capitalize()

				elif "VAKIO PROSESSORIJÄÄHDYTIN" in trimmed_name.upper():
					trimmed_name = trimmed_name.upper().strip("VAKIO PROSESSORIJÄÄHDYTIN").strip().rstrip("-").strip().lstrip("-").strip().capitalize()
					trimmed_name = "Intel stock cooler" + trimmed_name

				if any(s in desc.upper() for s in ["YHTEENSOPIVUUS"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if compatibility is None:
						compatibility = desc

				if any(s in desc.upper() for s in ["TDP"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if cooling_potential is None:
						cooling_potential = desc

				if any(s in desc.upper() for s in ["NOPEUS", "RPM"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if fan_rpm is None:
						fan_rpm = desc

				if any(s in desc.upper() for s in ["MELU", "DBA"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if noise_level is None:
						noise_level = desc

				if any(s in desc.upper() for s in ["MITAT", "KXLXS", "LXPXK"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if dimensions is None:
						dimensions = desc

			else:
				print("Something went wrong. Category:", get_category)

		# Create a dictionary with all of the chosen data
		part_lists_dict = {
			"storage_list": [capacity, form_factor, interface, cache, flash, tbw],
			"mobo_list": [chipset, form_factor, memory_compatibility],
			"case_list": [case_type, dimensions, color, compatibility],
			"ram_list": [mem_type, amount, speed, latency],
			"gpu_list": [cores, clock, memory, interface, dimensions, tdp],
			"cpu_list": [core_count, thread_count, base_clock, cpu_cache, socket, cpu_cooler, tdp, igpu],
			"psu_list": [atx12v, efficiency, modular, dimensions],
			"cooler_list": [compatibility, cooling_potential, fan_rpm, noise_level, dimensions],
		}

		# Choose the correct dictionary
		if part_type == "storage":
			item_list = part_lists_dict["storage_list"]
		elif part_type == "mobo":
			item_list = part_lists_dict["mobo_list"]
		elif part_type == "case":
			item_list = part_lists_dict["case_list"]
		elif part_type == "ram":
			item_list = part_lists_dict["ram_list"]
		elif part_type == "gpu":
			item_list = part_lists_dict["gpu_list"]
		elif part_type == "cpu":
			item_list = part_lists_dict["cpu_list"]
		elif part_type == "psu":
			item_list = part_lists_dict["psu_list"]
		elif part_type == "cooler":
			item_list = part_lists_dict["cooler_list"]

		item_list = trim_list(item_list)
		#pprint(item_list)

		# Final trimming
		if part_type == "gpu" and item_list[5] and item_list[5] != None:
			if "VÄHINTÄÄN" in item_list[5].upper():
				item_list[5] = item_list[5].upper().strip("VÄHINTÄÄN")

		if part_type == "mobo" and item_list[2] and item_list[2] != None:
			item_list[2] = item_list[2].strip(",")

		if part_type == "cpu" and item_list[0] and item_list[0] != None:
			item_list[0] = item_list[0].strip("-ydin")

		# Create final dictionaries for all parts, ready for database insertion
		if part_type == "storage":
			storage_dict = {
				"Url": curr_link,
				"Price": m_price,
				"Name": trimmed_name,
				"Manufacturer": m_manufacturer,
				"Capacity": item_list[0],
				"Form Factor": item_list[1],
				"Interface": item_list[2],
				"Cache": item_list[3],
				"Flash": item_list[4],
				"TBW": item_list[5],
			}
			pprint(storage_dict)
			i = insert(Storage).values(storage_dict)
			session.execute(i)
			session.commit()

		elif part_type == "mobo":
			mobo_dict = {
				"Url": curr_link,
				"Price": m_price,
				"Name": trimmed_name,
				"Manufacturer": m_manufacturer,
				"Chipset": item_list[0],
				"Form Factor": item_list[1],
				"Memory Compatibility": item_list[2],
			}
			pprint(mobo_dict)
			i = insert(Motherboard).values(mobo_dict)
			session.execute(i)
			session.commit()

		elif part_type == "case":
			case_dict = {
				"Url": curr_link,
				"Price": m_price,
				"Name": trimmed_name,
				"Manufacturer": m_manufacturer,
				"Case type": item_list[0],
				"Dimensions": item_list[1],
				"Color": item_list[2],
				"Compatibility": item_list[3],

			}
			pprint(case_dict)
			i = insert(Case).values(case_dict)
			session.execute(i)
			session.commit()

		elif part_type == "ram":
			ram_dict = {
				"Url": curr_link,
				"Price": m_price,
				"Name": trimmed_name,
				"Manufacturer": m_manufacturer,
				"Type": item_list[0],
				"Amount": item_list[1],
				"Speed": item_list[2],
				"Latency": item_list[3],
			}
			pprint(ram_dict)
			i = insert(Memory).values(ram_dict)
			session.execute(i)
			session.commit()

		elif part_type == "gpu":
			gpu_dict = {
				"Url": curr_link,
				"Price": m_price,
				"Name": trimmed_name,
				"Manufacturer": m_manufacturer,
				"Cores": item_list[0],
				"Core Clock": item_list[1],
				"Memory": item_list[2],
				"Interface": item_list[3],
				"Dimensions": item_list[4],
				"TDP": item_list[5],
			}
			pprint(gpu_dict)
			i = insert(GPU).values(gpu_dict)
			session.execute(i)
			session.commit()

		elif part_type == "cpu":
			cpu_dict = {
				"Url": curr_link,
				"Price": m_price,
				"Name": trimmed_name,
				"Manufacturer": m_manufacturer,
				"Core Count": item_list[0],
				"Thread Count": item_list[1],
				"Base Clock": item_list[2],
				"Cache": item_list[3],
				"Socket": item_list[4],
				"Cpu Cooler": item_list[5],
				"TDP": item_list[6],
				"Integrated GPU": item_list[7],
			}
			pprint(cpu_dict)
			i = insert(CPU).values(cpu_dict)
			session.execute(i)
			session.commit()

		elif part_type == "psu":
			psu_dict = {
				"Url": curr_link,
				"Price": m_price,
				"Name": trimmed_name,
				"Manufacturer": m_manufacturer,
				"Is ATX12V": item_list[0],
				"Efficiency": item_list[1],
				"Modular": item_list[2],
				"Dimensions": item_list[3],
			}
			pprint(psu_dict)
			i = insert(PSU).values(psu_dict)
			session.execute(i)
			session.commit()

		elif part_type == "cooler":
			cooler_dict = {
				"Url": curr_link,
				"Price": m_price,
				"Name": trimmed_name,
				"Manufacturer": m_manufacturer,
				"Compatibility": item_list[0],
				"Cooling Potential": item_list[1],
				"Fan RPM": item_list[2],
				"Noise Level": item_list[3],
				"Dimensions": item_list[4],
			}
			pprint(cooler_dict)
			i = insert(Cooler).values(cooler_dict)
			session.execute(i)
			session.commit()

		sleep(0.1)

main()