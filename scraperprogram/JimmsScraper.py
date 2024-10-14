# File name: dev_scraper.py
# Auth: Benjamin Willför/TerminalSwagDisorder, Sami Wazni & Alexander Willför
# Desc: File currently in development containing code for a scraper for jimms.com

import database
import requests
import time
import threading
import traceback
from pathlib import Path
from bs4 import BeautifulSoup
from time import sleep as sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException
from pprint import pprint as pprint
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import table, column, select, update, insert, delete, text
from sqlalchemy import create_engine



def main():
	# Timer for whole program
	program_start = time.time()
	
	# License notice
	print("This program uses the GNU General Public License (GPL) version 3")
	
	# Urls for jimms
	base_url = "https://www.jimms.fi"
	product_url = "/fi/Product/Show/"
	component_url = ["/fi/Product/List/000-00H/komponentit--emolevyt", "/fi/Product/List/000-00P/komponentit--naytonohjaimet"]
	#component_url = ["/fi/Product/List/000-00K/komponentit--kiintolevyt-ssd-levyt", "/fi/Product/List/000-00H/komponentit--emolevyt", "/fi/Product/List/000-00J/komponentit--kotelot", "/fi/Product/List/000-00N/komponentit--muistit", "/fi/Product/List/000-00P/komponentit--naytonohjaimet", "/fi/Product/List/000-00R/komponentit--prosessorit", "/fi/Product/List/000-00U/komponentit--virtalahteet", "/fi/Product/List/000-104/jaahdytys-ja-erikoistuotteet--jaahdytyssiilit"]
	
	# Initialize directory path
	dirPath = Path(__file__).resolve().parent

	# Do a speedtest to jimms
	speed_passed = speedtest(base_url)
	if not speed_passed:
		speed_input = input(f"Speedtest either failed or was low, do you still want to continue? (Y/yes) \n")

		if speed_input.upper() in ["Y", "YES"]:
			print("Continuing...")
		else:
			print("Stopping...")
			return
		
	imgDirPath = create_image_folder(dirPath)
	
	engine, session, metadata, CPU, GPU, Cooler, Motherboard, Memory, Storage, PSU, Chassis = database_connection()

	index_pages_dict = get_subpages(dirPath, base_url, component_url)
	all_product_links = get_urls(base_url, index_pages_dict)
	sleep(0.25)
	scraper_start = time.time()
	data_scraper(base_url, all_product_links, engine, session, metadata, CPU, GPU, Cooler, Motherboard, Memory, Storage, PSU, Chassis, imgDirPath)
	session.close()
	
	scraper_end = time.time()
	scraper_time = scraper_end - scraper_start
	print(f"\n\nScraper time: {scraper_time:.2f}")
	
	print("Scraping completed\n")
	
	program_end = time.time()
	program_time = program_end - program_start
	print(f"The program ran for {program_time:.2f} seconds!")
	
def create_image_folder(dirPath):
	# Create image folder if it does not exist
	imgDirPath = dirPath.joinpath("product_images")

	if not imgDirPath.exists():
		imgDirPath.mkdir()
	
	return imgDirPath

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
	# Do a speedtest to jimms
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
	# Create the tables
	engine, session, metadata = database.create_database()
	
	UniversalComponents_conn = database.UniversalComponents()
	CPU_conn = database.CPU()
	GPU_conn = database.GPU()
	Cooler_conn = database.Cooler()
	Motherboard_conn = database.Motherboard()
	Memory_conn = database.Memory()
	Storage_conn = database.Storage()
	PSU_conn = database.PSU()
	Chassis_conn = database.Chassis()
	
	database.Base.metadata.create_all(engine)
	

	CPU = database.CPU.__table__

	GPU = database.GPU.__table__

	Cooler = database.Cooler.__table__

	Motherboard = database.Motherboard.__table__

	Memory = database.Memory.__table__

	Storage = database.Storage.__table__

	PSU = database.PSU.__table__

	Chassis = database.Chassis.__table__

	return engine, session, metadata, CPU, GPU, Cooler, Motherboard, Memory, Storage, PSU, Chassis



def get_meta(item_soup, metasearch):
	# Get metadata data, usually most accurate
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
			
			# Trim each item by removing the colon and everything in it
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


def final_trim(part_type, item_list, item_position, keyword):
	# Final universal trimming
	if part_type and item_list[item_position] and item_list[item_position] != None:
		item_list_trimmed = item_list[item_position].upper().replace(keyword, "").strip().capitalize()
		
		return item_list_trimmed

def process_subpages(dirPath, base_url, index_pages_dict, item):
	# Create selenium instance
	cDriverPath = dirPath.joinpath("chromedriver-win64")
	chromeDirPath = dirPath.joinpath("chrome-win64")
	chromeFilePath = chromeDirPath.joinpath("chrome.exe")
	
	driver_path = cDriverPath.joinpath("chromedriver.exe")
	service = Service(driver_path)
	
	options = webdriver.ChromeOptions()
	options.binary_location = str(chromeFilePath)
	
	
	# In case there are SSL or similar errors hindering the code, use this
	#options.add_argument("--ignore-certificate-errors")
	#options.add_argument("--ignore-ssl-errors")
	#options.add_argument("--disable-proxy-certificate-handler")
	#options.add_argument("--disable-content-security-policy")
	
	driver = webdriver.Chrome(service = service, options = options)
	
	# In case you do not want to use chrome options
	#driver = webdriver.Chrome(service = service)
	
	
	
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
		sleep(1)

		# Get the url
		last_page_url = driver.current_url
		last_page_number = int(last_page_url.split("=")[-1])
		page_index.append(last_page_number)

		# Add subpage numbers to page_index
		page_nums = range(page_index[0] + 1, page_index[1])
		for num in page_nums:
			page_index.append(num)
			page_index.sort()

		# Create a new list with added parameter
		pages_with_param = [parameter + str(page) for page in page_index]

		# Create a list/dictionary with all subpages
		index_pages_dict[item] = [parameter + str(page) for page in page_index]

	except Exception as e:
		print(f"Error while processing {item}: {e}")	
	finally:
		driver.close()
		driver.quit()

def get_subpages(dirPath, base_url, component_url):
	# Get all of the component subpages, ie, cpu page 1, cpu page 2 etc
	index_pages_dict = {}

	threads = []

	for item in component_url:
		# Speed the process up
		thread = threading.Thread(target=process_subpages, args=(dirPath, base_url, index_pages_dict, item))
		thread.start()
		threads.append(thread)

	for thread in threads:
		thread.join()


	print("All subpages scraped")
	return index_pages_dict

def process_url(curr_url, all_product_links, lock):
	try:
		# Add a lock to the threading to keep the parts ordered
		lock.acquire()
		# Parse and iterate through the html using bs4
		product_list_page = requests.get(curr_url)
		next_soup = BeautifulSoup(product_list_page.content, "html.parser")
		page_content = next_soup.find("div", class_="product-list-wrapper")
		product_name = page_content.find_all("h5", class_="product-box-name")
		lock.release()
		
		# Get the actual link for each item
		for item in product_name:
			if "TARJOUS" not in item.text.upper() and "BUNDLE" not in item.text.upper() and "OUTLET" not in item.text.upper():
				lock.acquire()
				product_link = item.find("a", href=True)
				get_link = product_link.get("href")
				
				all_product_links.append(get_link)
				lock.release()
				
				sleep(0.1)
			else:
				print("Skipped reduced or bundled item")
			
	except Exception as e:
		print(f"Error while processing {curr_url}: {e}")
	else:
		print(f"{len(all_product_links)} links found")	


def get_urls(base_url, index_pages_dict):
	# Get the urls of all products from the subpages
	url_start = time.time()
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
	
	url_end = time.time()
	url_time = url_end - url_start
	print(f"Url time: {url_time:.2f}\nFinal amount of valid links: {len(all_product_links)}\n")
	sleep(0.1)
	return all_product_links

def get_image(part_type, product_image, imgDirPath):
	# Download product images
	image_file = Path(f"{part_type.upper()}_{product_image.split('/')[-1]}").name
	file_path = imgDirPath.joinpath(image_file)

	img_response = requests.get(product_image)
	if img_response.status_code == 200:
		with open(file_path, "wb") as f:
			f.write(img_response.content)
			return image_file
	else:
		print(f"Failed to download: {image_file}")
		return None


def data_scraper(base_url, all_product_links, engine, session, metadata, CPU, GPU, Cooler, Motherboard, Memory, Storage, PSU, Chassis, imgDirPath):
	# All of the data scraping in each product page
	for product in all_product_links:
		try:
			desc_list = []
			curr_link = base_url + product

			item_page = requests.get(curr_link, allow_redirects=True)
			item_soup = BeautifulSoup(item_page.content, "html.parser")

			# Get product categories of varying importance
			category_link = item_soup.find_all("a", class_="link-secondary")[2]
			get_category = category_link.get("href")
			
			try:
				type_link = item_soup.find_all("a", class_="link-secondary")[3]
				get_type = type_link.get("href")
				type_text = type_link.get_text()
				
			except:
				print("Cannot get product type link")
				
			try:
				spec_link = item_soup.find_all("a", class_="link-secondary")[4]
				get_spec = spec_link.get("href")
				spec_text = spec_link.get_text()
			except:
				print("Cannot get product spec link")


			# Getting some data with metadata
			m_manufacturer = get_meta(item_soup, {"property": "product:brand"})
			m_price = get_meta(item_soup, {"property": "product:price:amount"})
			m_desc = get_meta(item_soup, {"property": "og:description"})
			m_image = get_meta(item_soup, {"property": "og:image"})
			
			# Get the image shown in the page first
			product_image = item_soup.find(class_="product-gallery").find("img")
			if product_image:
				product_image = product_image.get("src")
			else:
				product_image = m_image
				print(f"No image found in the item page, using the metadata og image")
				
			if product_image.startswith("//") and not product_image.startswith("http"):
				product_image = f"https:{product_image}"
			elif not product_image.startswith("//") and not product_image.startswith("http"):
				product_image = f"https://{product_image}"

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
			#desc_data = results_item.select_one("strong:-soup-contains('Tekniset tiedot')") # Default
			#desc_data = results_item.select_one(":contains('Tekniset tiedot')")
			#if desc_data:
			if results_item:
				trimmed_data_p = results_item.contents

				for sibling in trimmed_data_p:
					if sibling is not None and sibling != "":

						# In case there is a ul item, get it separately
						if sibling.name == "ul":

							ul_title = sibling.find_previous_sibling()
							if ul_title:
								ul_title = ul_title.get_text("\n").strip("\xa0-").strip().splitlines()
								while True:
									if ul_title[-1] == ":" or ul_title[-1] == "":
										del ul_title[-1]
									else:
										ul_title = ul_title[-1]
										break
									
								if ":" not in ul_title:
									ul_title = ul_title + ":"
							else:
								ul_title = None


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
								except Exception as e:
									traceback_str = traceback.format_exc()
									print(f"Something went wrong: {traceback_str}")


						else:
							# If the item is not a ul item
							sibling_trim = sibling.get_text("\n")
							tt_trim = sibling_trim.strip("\xa0-").strip()
							newline_trim = tt_trim.splitlines()
							if len(newline_trim) > 0 and newline_trim != "":
								i = 0
								for final_item in newline_trim:
									final_item = final_item.strip()
									if ":N" in final_item.upper():
										final_item = final_item.upper().replace(":N", "")
									if "\xa0-" in final_item or "\XA0-" in final_item:
										final_item = final_item.replace("\xa0-", "").strip()
										final_item = final_item.replace("\XA0-", "").strip()
									if final_item.startswith("-"):
										if ":" in final_item:
											final_item = final_item.replace("-", "", 1).strip()
										elif ":" not in final_item:
											final_item = final_item.replace("-", ":", 1).strip()
									desc_list.append(final_item)


					# Remove all empty items from desc_list
					desc_list = [x for x in desc_list if x != ""]


					# Remove everything before the specs
					#if any("Tekniset tiedot:" in s or "Tekniset tiedot" in s for s in desc_list) or "Tekniset tiedot" in desc_list or "Tekniset tiedot:" in desc_list:
					#if any(s in (i.upper() for i in desc_list) for s in ["TEKNISET TIEDOT:", "TEKNISET TIEDOT"]):
					#if any(s in [i.upper() for i in desc_list] for s in ["TEKNISET TIEDOT:", "TEKNISET TIEDOT"]):
					if any(s.upper() in x.upper() for x in desc_list for s in ["TEKNISET TIEDOT:", "TEKNISET TIEDOT"]):
						index = 0
						if "Tekniset tiedot" in desc_list:
							index = desc_list.index("Tekniset tiedot")

						elif "Tekniset tiedot:" in desc_list:
							index = desc_list.index("Tekniset tiedot:")
							
						if len(desc_list) > index + 2 and len(desc_list) > 5:
							if desc_list[index + 1] == ":":
								desc_list = desc_list[index + 2:]
							elif desc_list[index + 1] != ":":
								desc_list = desc_list[index + 1:]
							else:
								desc_list = desc_list[index:]


					
					# For pages with separate colons, combine the previous string and next string with the colon
					for i, item in enumerate(desc_list):
						if item == ":" and not desc_list[i-1].endswith(":"):
							desc_list[i] = desc_list[i-1] + item
							del desc_list[i-1]
							
					# Remove all remaining ":" and Tekniset tiedot	
					#desc_list = [x for x in desc_list if x != "" and x != ":" and x != "Tekniset tiedot" and x != "Tekniset tiedot:"]
					desc_list = [x for x in desc_list if x != "" and x != ":"]

					# Format items better
					try:
						for i, item in enumerate(desc_list):
							if "TEKNISET TIEDOT" in desc_list[i].upper():
								continue
								#del desc_list[i]
							if i != 0 and item.startswith(":"):
								desc_list[i] = desc_list[i-1] + desc_list[i]
								del desc_list[i-1]

							elif i+1 < len(desc_list) and item.endswith(":"):
								desc_list[i] = desc_list[i] + desc_list[i+1]
								del desc_list[i+1]

							if i+1 < len(desc_list) and "PROSESSORITUKI" in desc_list[i].upper() and ":" not in desc_list[i+1] and not any(s in desc_list[i+1].upper() for s in ["TUKEE", "SERIES", "SARJA", "SARJAN", "SUKUPOLVEN"]):
								if any(s in desc_list[i].upper() for s in ["TUKEE", "SERIES", "SARJA", "SARJAN", "SUKUPOLVEN"]):
									desc_list[i] = desc_list[i].split(":", 1)[0] + ":"

								desc_list[i] = desc_list[i] + desc_list[i+1]
								del desc_list[i+1]
								
					except IndexError as e:
						traceback_str = traceback.format_exc()
						print(f"Error: {traceback_str}")
					except Exception as e:
						traceback_str = traceback.format_exc()
						print(f"Something went wrong: {traceback_str}")
				sleep(0.1)

		except Exception as e:
			traceback_str = traceback.format_exc()
			print(f"Something went wrong: {traceback_str}")
			

		#pprint(name_list)
		#pprint(desc_list)
		#print(type_text)


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
		chassis_type = None
		dimensions = None
		color = None
		compatibility = None
		cpu_compatibility = None
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
		intel_lga = None
		amd_am = None
		trimmed_type = None


		# Depending on what category is active, sort the data to the respective variables
		for desc in desc_list:

			if "/fi/Product/List/000-00K" in get_category:
				part_type = "storage"

				if "SSD-LEVY" in trimmed_name.upper():
					trimmed_name = trimmed_name.upper().replace("SSD-LEVY", "").strip().capitalize()
				
				if any(s in desc.upper() for s in ["KAPASITEETTI", "MUISTIN KOKO"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if capacity is None:
						capacity = desc
					
				elif any(s in desc.upper() for s in ["FORM FACTOR:", "M.2 TYYPPI", "MUOTO", "YHTEENSOPIVA PAIKKA"]) and ":" in desc.upper() and not desc.strip().endswith(":") and "OMINAISUUDET" not in desc.upper():
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

				elif any(s in desc.upper() for s in ["TBW", "KÄYTTÖKESTÄVYYS", "TOTAL BYTES WRITTEN", "KESTOKYKY", "KESTÄVYYS"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if tbw is None:
						tbw = desc


			elif "/fi/Product/List/000-00H" in get_category:
				part_type = "mobo"

				if any(s in desc.upper() for s in ["PIIRISARJA"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if chipset is None:
						chipset = desc
						
				elif any(s in desc.upper() for s in ["PROSESSORITUKI", "PROSESSORI"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if cpu_compatibility is None:
						cpu_compatibility = desc		
				
				elif any(s in desc.upper() for s in ["TUOTTEEN TYYPPI", "EMOLEVYN TYYPPI"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if form_factor is None:
						form_factor = desc
						
				elif any(s in desc.upper() for s in ["DIMM", "MUISTI", "MUISTITUKI"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if memory_compatibility is None:
						memory_compatibility = desc


			elif "/fi/Product/List/000-00J" in get_category:
				part_type = "chassis"

				if any(s in desc.upper() for s in ["KOTELOTYYPPI", "TYYPPI", "FORM FACTOR", "KOTELON TYYPPI"]) and ":" in desc.upper() and not desc.strip().endswith(":") and not any(s in desc.upper() for s in ["VIRTALÄH", "MATERIA", "LEVYTUKI"]):
					if chassis_type is None:
						chassis_type = desc

				elif "MAKSIMIMITAT" not in desc.upper() and any(s in desc.upper() for s in ["LXWXH", "L X W X H", "PXLXK", "(PXLXK)", "KXLXS", "LXPXK", "L X K X S",  "KXPXL", "SXLXK", "(LXKXS)", "(KXLXS)", "MITAT", "DIMENSION", "ULOKKEINEEN"]) and ":" in desc.upper() and not desc.strip().endswith(":") and not any(s in desc.upper() for s in ["LITRA", "MATERIA"]) or "KOTELO" in desc.upper() and "MM" in desc.upper() and ":" in desc.upper() and not desc.strip().endswith(":"):
					if dimensions is None:
						dimensions = desc

				elif any(s in desc.upper() for s in ["VÄRI", "VÄRI(T)", "COLOR", "COLOUR", "VIIMEISTELY"]) and ":" in desc.upper() and not desc.strip().endswith(":") and not any(s in desc.upper() for s in ["RGB"]):
					if color is None:
						color = desc

				elif any(s in desc.upper() for s in ["YHTEENSOPIVUUS", "ATX", "ITX", "EMOLEVYT", "MOTHERBOARD", "MOTHERBOARDS", "SOPIVUUS", "PÄÄSIJAINEN"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if compatibility is None:
						compatibility = desc


			elif "/fi/Product/List/000-00N" in get_category:
				part_type = "ram"
				
				if any(s in desc.upper() for s in ["TYYPPI", "TEKNIIKKA"]) and ":" in desc.upper() and not desc.strip().endswith(":") and not any(s in desc.upper() for s in ["PÄIVITYS"]):
					if mem_type is None:
						if any(s in desc.upper() for s in ["TEKNIIKKA"]):
							mem_type = desc
						elif any(s in desc.upper() for s in ["TYYPPI"]) and any(s in desc.upper() for s in ["DDR"]) and not any(s in desc.upper() for s in ["PÄIVITYS"]):
							mem_type = desc

				elif any(s in desc.upper() for s in ["KAPASITEETTI", "CAPACITY", "KAPASISTEETTI"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if amount is None:
						amount = desc

				elif any(s in desc.upper() for s in ["NOPEUS", "SPEED", "TAAJUUS"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if speed is None:
						speed = desc

				elif any(s in desc.upper() for s in ["LATENSSI", "LATENCY", "CAS"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if latency is None:
						latency = desc


			elif "/fi/Product/List/000-00P" in get_category:
				part_type = "gpu"

				if "NÄYTÖNOHJAIN" in trimmed_name.upper():
					trimmed_name = trimmed_name.upper().replace("NÄYTÖNOHJAIN", "").strip().rstrip("-").strip().lstrip("-").strip().capitalize()

				if any(s in desc.upper() for s in ["CUDA", "STREAM-PROSESSORIT", "CORET", "XMX"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if cores is None:
						cores = desc

				elif any(s in desc.upper() for s in ["BOOST", "KELLOTAAJUUS", "DEFAULT MODE"]) and any(s in desc.upper() for s in ["GHZ", "MHZ"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if clock is None:
						clock = desc

				elif any(s in desc.upper() for s in ["MUISTI"]) and ":" in desc.upper() and not desc.strip().endswith(":") or any(s in desc.upper() for s in ["KOKO", "MÄÄRÄ"]) and any(s in desc.upper() for s in ["GB", "DDR", "MB"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if memory is None:
						if any(s in desc.upper() for s in ["KOKO", "MÄÄRÄ"]) and any(s in desc.upper() for s in ["GB", "DDR", "MB"]):
							memory = desc
						else:
							memory = None
							desc = desc
						if any(s in desc.upper() for s in ["MUISTI"]):
							memory = desc

				elif any(s in desc.upper() for s in ["VÄYLÄ", "PCI EXPRESS KONFIG"]) and not "MUISTIVÄYLÄ" in desc.upper() and ":" in desc.upper() and not desc.strip().endswith(":"):
					if interface is None:
						interface = desc

				elif any(s in desc.upper() for s in ["MITAT", "PITUUS", "KXLXS", "LXPXK"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if dimensions is None:
						dimensions = desc

				elif any(s in desc.upper() for s in ["TDP", "VIRTALÄHTE", "TEHONKULUTUS", "VIRRANKULUTUS", "VIRRAN KULUTUS", "TEHON KULUTUS", "TBP"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
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

				elif any(s in desc.upper() for s in ["KELLOTAAJUUS", "BASE CLOCK"]) and ":" in desc.upper() and not desc.strip().endswith(":") or any(s in desc.upper() for s in ["BASE"]) and any(s in desc.upper() for s in ["GHZ"]) and not any(s in desc.upper() for s in ["W", "BASE POWER", "TDP"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if base_clock is None:
						if any(s in desc.upper() for s in ["BASE"]) and any(s in desc.upper() for s in ["GHZ"]) and not any(s in desc.upper() for s in ["W", "BASE POWER", "TDP"]):
							base_clock = desc
						else:
							base_clock = None
							desc = desc
						if any(s in desc.upper() for s in ["KELLOTAAJUUS", "BASE CLOCK"]):
							base_clock = desc

				elif any(s in desc.upper() for s in ["VÄLIMUISTI", "L3"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if cpu_cache is None:
						cpu_cache = desc

				elif any(s in desc.upper() for s in ["KANTA", "YHTEENSOPIVUUS"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if socket is None:
						socket = desc

				elif any(s in desc.upper() for s in ["JÄÄHDYTYS", "YHTEENSOPIVUUS", "JÄÄHDYTIN"]) and not "EI SIS" in desc.upper() and ":" in desc.upper() and not desc.strip().endswith(":"):
					if cpu_cooler is None:
						cpu_cooler = desc

				elif any(s in desc.upper() for s in ["TDP", "THERMAL DESIGN POWER", "BASE POWER"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
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

				elif any(s in desc.upper() for s in ["80 PLUS", "HYÖTYSUHDE", "TEHOKKUUS", "80PLUS"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if efficiency is None:
						efficiency = desc

				elif any(s in desc.upper() for s in ["MODULAR", "MODULAARI"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if modular is None:
						if "TÄYSIN" in desc.upper() or "TÄYSI" in desc.upper() or "FULL" in desc.upper():
							modular = "Fully modular"
						elif "SEMI" in desc.upper():
							modular = "Semi modular"
						else:
							modular = desc

				elif any(s in desc.upper() for s in ["KOKO", "MITAT", "KXLXS", "LXPXK", "PXLXK", "KXLXP", "LXKXS", "K X L X S", "L X P X K", "P X L X K", "K X L X P", "L X K X S"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if dimensions is None:
						dimensions = desc


			elif "/fi/Product/List/000-104" in get_category and "/fi/Product/List/000-059" in get_type:
				part_type = "cooler"

				if "PROSESSORIJÄÄHDYTIN" in trimmed_name.upper():
					trimmed_name = trimmed_name.upper().replace("PROSESSORIJÄÄHDYTIN", "").strip().rstrip("-").strip().lstrip("-").strip().capitalize()

				elif "VAKIO PROSESSORIJÄÄHDYTIN" in trimmed_name.upper():
					trimmed_name = trimmed_name.upper().replace("VAKIO PROSESSORIJÄÄHDYTIN", "").strip().rstrip("-").strip().lstrip("-").strip().capitalize()
					trimmed_name = "Intel stock cooler" + trimmed_name

				if any(s in desc.upper() for s in ["YHTEENSOPIVUUS", "KANNAT", "COMPATIBILITY", "KANTA", "SOCKET"]) and ":" in desc.upper() and not desc.strip().endswith(":") or any(s in desc.upper() for s in ["INTEL", "AMD"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if desc.strip().startswith(":"):
						desc = desc.replace(":", "", 1)
					if any(s in desc.upper() for s in ["INTEL"]) and any(s in desc.upper() for s in ["11", "12", "20", "17", "13", "77", "LGA"]):
						intel_lga = desc
					elif any(s in desc.upper() for s in ["AMD"]) and any(s in desc.upper() for s in ["AM", "FM"]):
						amd_am = desc
					if intel_lga and amd_am:
						compatibility = f"{intel_lga}; {amd_am}"
					elif intel_lga and not amd_am:
						compatibility = intel_lga
					elif amd_am and not intel_lga:
						compatibility = amd_am

					if compatibility is None:
						if any(s in desc.upper() for s in ["INTEL"]) and any(s in desc.upper() for s in ["AMD"]) and any(s in desc.upper() for s in ["11", "12", "20", "LGA"]) and any(s in desc.upper() for s in ["AM", "FM"]):
							compatibility = desc
						if any(s in desc.upper() for s in ["YHTEENSOPIVUUS", "KANNAT", "COMPATIBILITY", "KANTA", "SOCKET"]):	
							compatibility = desc

				if any(s in desc.upper() for s in ["TDP"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if cooling_potential is None:
						if "KATSO VALMISTAJAN" in desc.upper():
							cooling_potential = None
						else:
							cooling_potential = desc

				if any(s in desc.upper() for s in ["NOPEUS", "RPM", "SPEED"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if fan_rpm is None:
						fan_rpm = desc

				if any(s in desc.upper() for s in ["MELU", "DBA", "NOISE"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if noise_level is None:
						noise_level = desc

				if any(s in desc.upper() for s in ["MITAT", "KXLXS", "LXPXK", "DIMENSIONS", "KOKO", "K X L X S", "L X P X K"]) and ":" in desc.upper() and not desc.strip().endswith(":"):
					if dimensions is None:
						dimensions = desc


			else:
				part_type = "invalid"
				print("Something went wrong. Category:", get_category)
				break
				

		if part_type and part_type != "invalid":
			# Additional data for some cases for when no applicable data was found in the loop
			if part_type == "storage":
				if form_factor is None:
					if "SATA III -LEVYT" in type_text.upper():
						trimmed_type = type_text.upper().replace("SATA III -LEVYT", '3.5"')
					elif "SSD-LEVYT M.2" in type_text.upper():
						trimmed_type = type_text.upper().replace("SSD-LEVYT M.2", "M.2")
					elif 'SSD-LEVYT 2.5"' in type_text.upper():
						trimmed_type = type_text.upper().replace('SSD-LEVYT 2.5"', '2.5"')
					elif "SSD-LEVYT MSATA" in type_text.upper():
						trimmed_type = type_text.upper().replace("SSD-LEVYT MSATA", "mSATA")
					elif "SSD-KORTIT PCI-E" in type_text.upper():
						trimmed_type = type_text.upper().replace("SSD-KORTIT PCI-E", "PCI-E")
					elif "SCSI -LEVYT" in type_text.upper():
						trimmed_type = type_text.upper().replace("SCSI -LEVYT", "SCSI")

					form_factor = trimmed_type

			elif part_type == "ram":
				if mem_type is None:
					mem_type = type_text
				if amount is None and spec_text and any(s in spec_text.upper() for s in ["GB"]):
					amount = spec_text
			
			elif part_type == "chassis":
				if chassis_type is None:
					chassis_type = type_text
	
			elif part_type == "psu":
				if modular is None and get_type == "/fi/Product/List/000-188":
					modular = "Modular"
				elif modular is None and get_type == "/fi/Product/List/000-187":
					modular = "False"
					

			# Create a dictionary with all of the chosen data
			part_lists_dict = {
				"storage_list": [capacity, form_factor, interface, cache, flash, tbw],
				"mobo_list": [chipset, cpu_compatibility, form_factor, memory_compatibility],
				"chassis_list": [chassis_type, dimensions, color, compatibility],
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
			elif part_type == "chassis":
				item_list = part_lists_dict["chassis_list"]
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
					item_list[5] = item_list[5].upper().replace("VÄHINTÄÄN", "").strip()
					
			if part_type == "mobo":
				item_list[3] = final_trim(part_type, item_list, 3, ",")
				item_list[0] = final_trim(part_type, item_list, 0, ":")
				item_list[1] = final_trim(part_type, item_list, 1, "AMD")
				item_list[1] = final_trim(part_type, item_list, 1, "INTEL")
				item_list[3] = final_trim(part_type, item_list, 3, "MUISTIARKITEKTUURI")
				item_list[3] = final_trim(part_type, item_list, 3, "-")
			elif part_type == "cpu":
				item_list[0] = final_trim(part_type, item_list, 0, "-YDIN")
				item_list[0] = final_trim(part_type, item_list, 0, "-YTIMINEN")
				item_list[1] = final_trim(part_type, item_list, 1, "SÄIETTÄ")
				item_list[6] = final_trim(part_type, item_list, 6, "(PROCESSOR BASE POWER)")
				item_list[4] = final_trim(part_type, item_list, 4, "SOCKET")
			elif part_type == "gpu":
				item_list[1] = final_trim(part_type, item_list, 1, "JOPA")
				item_list[1] = final_trim(part_type, item_list, 1, "ENINTÄÄN")
				item_list[3] = final_trim(part_type, item_list, 3, "ENINTÄÄN")
				item_list[0] = final_trim(part_type, item_list, 0, "ENINTÄÄN")
				item_list[0] = final_trim(part_type, item_list, 0, "YKSIKKÖÄ")
				item_list[1] = final_trim(part_type, item_list, 1, "GAMING MODE:")
			elif part_type == "cooler":
				item_list[0] = final_trim(part_type, item_list, 0, ":SOPII")
				item_list[0] = final_trim(part_type, item_list, 0, "SOPII")
				item_list[0] = final_trim(part_type, item_list, 0, "YHTEENSOPIVUUS:")
				item_list[0] = final_trim(part_type, item_list, 0, "YHTEENSOPIVUUS")
				if item_list[0] is not None and item_list[0].strip().startswith(":"):
					item_list[0] = final_trim(part_type, item_list, 0, ":")
			elif part_type == "ram":
				item_list[0] = final_trim(part_type, item_list, 0, ",")
			elif part_type == "storage":
				item_list[1] = final_trim(part_type, item_list, 1, "FORM FACTOR:")
				item_list[0] = final_trim(part_type, item_list, 0, "KAPASITEETTI:")
			elif part_type == "chassis":
				item_list[1] = final_trim(part_type, item_list, 1, "PXLXK:")


			image_file = get_image(part_type, product_image, imgDirPath)


			# Create final dictionaries for all parts, ready for database insertion
			if part_type == "storage":
				storage_dict = {
					"Url": curr_link,
					"Price": m_price,
					"Name": trimmed_name,
					"Manufacturer": m_manufacturer,
					"Image": image_file,
					"Image_Url": product_image,
					"Capacity": item_list[0],
					"Form_Factor": item_list[1],
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
					"Image": image_file,
					"Image_Url": product_image,
					"Chipset": item_list[0],
					"Cpu_Compatibility": item_list[1],
					"Form_Factor": item_list[2],
					"Memory_Compatibility": item_list[3],
				}
				#pprint(mobo_dict)
				i = insert(Motherboard).values(mobo_dict)
				session.execute(i)
				session.commit()

			elif part_type == "chassis":
				chassis_dict = {
					"Url": curr_link,
					"Price": m_price,
					"Name": trimmed_name,
					"Manufacturer": m_manufacturer,
					"Image": image_file,
					"Image_Url": product_image,
					"Chassis_type": item_list[0],
					"Dimensions": item_list[1],
					"Color": item_list[2],
					"Compatibility": item_list[3],

				}
				pprint(chassis_dict)
				i = insert(Chassis).values(chassis_dict)
				session.execute(i)
				session.commit()

			elif part_type == "ram":
				ram_dict = {
					"Url": curr_link,
					"Price": m_price,
					"Name": trimmed_name,
					"Manufacturer": m_manufacturer,
					"Image": image_file,
					"Image_Url": product_image,
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
					"Image": image_file,
					"Image_Url": product_image,
					"Cores": item_list[0],
					"Core_Clock": item_list[1],
					"Memory": item_list[2],
					"Interface": item_list[3],
					"Dimensions": item_list[4],
					"TDP": item_list[5],
				}
				#pprint(gpu_dict)
				i = insert(GPU).values(gpu_dict)
				session.execute(i)
				session.commit()

			elif part_type == "cpu":
				cpu_dict = {
					"Url": curr_link,
					"Price": m_price,
					"Name": trimmed_name,
					"Manufacturer": m_manufacturer,
					"Image": image_file,
					"Image_Url": product_image,
					"Core_Count": item_list[0],
					"Thread_Count": item_list[1],
					"Base_Clock": item_list[2],
					"Cache": item_list[3],
					"Socket": item_list[4],
					"Cpu_Cooler": item_list[5],
					"TDP": item_list[6],
					"Integrated_GPU": item_list[7],
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
					"Image": image_file,
					"Image_Url": product_image,
					"Is_ATX12V": item_list[0],
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
					"Image": image_file,
					"Image_Url": product_image,
					"Compatibility": item_list[0],
					"Cooling_Potential": item_list[1],
					"Fan_RPM": item_list[2],
					"Noise_Level": item_list[3],
					"Dimensions": item_list[4],
				}
				pprint(cooler_dict)
				i = insert(Cooler).values(cooler_dict)
				session.execute(i)
				session.commit()


			sleep(0.1)
		else:
			print("Invalid part type!")

if __name__ == "__main__":
	main()