# File name: dev_scraper.py
# Auth: Benjamin Willför/TerminalSwagDisorder & Sami Wazni
# Desc: File currently in development containing code for a scraper for jimms.com

import database
import requests
from bs4 import BeautifulSoup
from time import sleep as sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pprint import pprint as pprint


def main():
	# Urls for jimms
	base_URL = "https://www.jimms.fi"
	product_URL = "/fi/Product/Show/"
	component_URL = ["/fi/Product/List/000-00H/komponentit--emolevyt"]
	component_URL2 = ["https://www.jimms.fi/fi/Product/Show/187728/tuf-rtx4070ti-o12g-gaming/asus-geforce-rtx-4070-ti-tuf-gaming-oc-edition-naytonohjain-12gb-gddr6x-asus-cashback-70"]
	component_temp = ["/fi/Product/List/000-00K/komponentit--kiintolevyt-ssd-levyt", "/fi/Product/List/000-00H/komponentit--emolevyt", "/fi/Product/List/000-00J/komponentit--kotelot", "/fi/Product/List/000-00M/komponentit--lisakortit", "/fi/Product/List/000-00N/komponentit--muistit", "/fi/Product/List/000-00P/komponentit--naytonohjaimet", "/fi/Product/List/000-00R/komponentit--prosessorit", "/fi/Product/List/000-00U/komponentit--virtalahteet"]
	## Note that component_URL is currently only for gpu. Just copy the contents of component_temp there if you want to do something with all parts
	driver_path = "./chromedriver_win32/chromedriver.exe"

	driver = webdriver.Chrome(executable_path=driver_path)
	
	index_pages_dict = get_subpages(base_URL, component_URL, driver)
	all_product_links = get_urls(base_URL, index_pages_dict)
	get_category, desc_list = data_scraper(base_URL, all_product_links)
	data_prep(get_category, desc_list)



def trim_list(item_list):
	for i, item in enumerate(item_list):
		if item and item != None:
			data = item.split(":", 1)
			if len(data) > 1:
				item_list[i] = data[1].strip().capitalize()
			else:
				item_list[i] = item.strip().capitalize()
	return item_list


def check_record_exists(session, main_parts, name):
	# Check if item exists in database
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
			
def get_subpages(base_URL, component_URL, driver):
	index_pages_dict = {}
	
	# Get subpages for all components
	try: 
		for item in component_URL:
			parameter = "?p="

			page_index = [1]

			print("Getting all pages for", item)

			# Go to page using Selenium
			driver.get(base_URL + item + "?p=1")
			wait = WebDriverWait(driver, 10)
			button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@data-bind='click: moveToLastPage']")))
			driver.execute_script("arguments[0].click();", button)
			sleep(2)

			# Get the URL
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

			sleep(2)
	except Exception as e:
		print(f"Error while processing {item}: {e}")
	else:
		print("All subpages scraped")


	driver.close()
	driver.quit()
	

	return index_pages_dict
	
def get_urls(base_URL, index_pages_dict):
	all_product_links = []
	
	# Get links for all the products
	for key, value in index_pages_dict.items():
		for index in value:
			curr_url = base_URL + key + index
			print(curr_url)
			
			# Parse and iterate through the html using bs4
			try: 
				product_list_page = requests.get(curr_url)
				next_soup = BeautifulSoup(product_list_page.content, "html.parser")
				page_content = next_soup.find("div", class_="product-list-wrapper")
				product_name = page_content.find_all("h5", class_="product-box-name")
				

				# Get the actual link for each item
				for item in product_name:
					if "Tarjous" not in item.text and "Bundle" not in item.text and "Outlet" not in item.text:
						product_link = item.find("a", href = True)
						get_link = product_link.get("href")

						all_product_links.append(get_link)
						#print(get_link)
						sleep(0.2)
					else:
						print("Skipped reduced or bundled item")
			except Exception as e:
				print(f"Error while processing {curr_url}: {e}")
			else:
				print(f"{len(all_product_links)} links found")
					

	return all_product_links

def data_scraper(base_URL, all_product_links):
	
	for product in all_product_links:
		curr_link = base_URL + product
		item_page = requests.get(curr_link, allow_redirects=True)
		item_soup = BeautifulSoup(item_page.content, "html.parser")
		
		# Get product category
		category_link = item_soup.find_all("a", class_="link-secondary")[2]
		get_category = category_link.get("href")


		## Testing getting the data with metadata
		# Get manufacturer 
		meta_manufacturer = item_soup.find("meta", {"property": "product:brand"})
		m_manufacturer = meta_manufacturer["content"]
		
		# Get price
		meta_price = item_soup.find("meta", {"property": "product:price:amount"})
		m_price = meta_price["content"]
		
		# Get description in different form
		meta_desc = item_soup.find("meta", {"property": "og:description"})
		m_desc = meta_desc["content"]


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

		# Get motherboard chipset from description
		chipset_location = results_item.select_one("strong:-soup-contains('Piirisarja')")
		chipset_list = []
		
		if chipset_location is not None:
			chipset_data = chipset_location.find_next_siblings(string = True)
			for item in chipset_data:
				if item != ":" and item is not None and item not in chipset_list:
					chipset_list.append(item)
			chipset_list = chipset_list[0]
		else:
			chipset_list = None
		
		# Get motherboard form factor from description
		ff_location = results_item.select_one("strong:-soup-contains('Emolevyn tyyppi')")
		ff_list = []
		
		if ff_location is not None:
			ff_data = ff_location.find_next_siblings(string = True)
			for item in ff_data:
				if item != ":" and item is not None and item not in ff_list:
					ff_list.append(item)
			ff_list = ff_list[0]
		else:
			ff_list = None
		
		# Get motherboard form factor from description
		mobo_memory_location = results_item.select_one("strong:-soup-contains('Muisti')")
		mobo_memory_list = []
		
		if mobo_memory_location is not None:
			mobo_memory_data = mobo_memory_location.find_next_siblings(string = True)
			for item in mobo_memory_data:
				if item != ":" and item is not None and item not in mobo_memory_list:
					mobo_memory_list.append(item)
			mobo_memory_list = mobo_memory_list[0]
			if "," in mobo_memory_list:
				mobo_memory_list = mobo_memory_list.split(",", 1)
				if len(mobo_memory_list) > 1:
					mobo_memory_list = mobo_memory_list[0].strip()
				else:
					mobo_memory_list = mobo_memory_list
		else:
			mobo_memory_list = None

		print(mobo_memory_list)


		
		# Get all of the description data and trim it
		print("Current page:", curr_link)
		desc_data = results_item.select_one("strong:-soup-contains('Tekniset tiedot')")
		if desc_data is not None:
			trimmed_data = desc_data.find_all_next(recursive = False)
			desc_list = []
			for item in trimmed_data:
				if item.name in ["div", "a"]:
					#print("break:", item.name)
					break

				elif item.name in ["p", "strong", "span", "li", "ul"]:
					for desc in item.stripped_strings:
						if desc and desc not in desc_list:
							#print(desc)
							desc_list.append(desc)
			sleep(0.1)
			#pprint(name_list)
			#pprint(desc_list)

			for desc in desc_list:
				trimmed_name = None
				capacity = None
				form_factor = None
				interface = None
				cache = None
				flash = None
				tbw = None
				chipset = None
				form_factor = None
				memory_compatibility = None
				cores = None
				clock = None
				memory = None
				interface = None
				size = None
				tdp = None
				core_count = None
				thread_count = None
				base_clock = None
				l3_cache = None
				socket = None
				cpu_cooler = None
				igpu = None
				
				## Into these if statements, do as i've done in the gpu part already
				if "/fi/Product/List/000-00K" in get_category:
					part_type = "storage"
					
					if "SSD-LEVY" in trimmed_name.upper():
						trimmed_name = trimmed_name.upper().strip("SSD-LEVY").strip().capitalize()
					
					if "KAPASITEETTI" in desc.upper():
						capacity = desc
					
					elif "FORM FACTOR" in desc.upper() or "M.2 TYYPPI" in desc.upper():
						form_factor = desc
					
					elif "VÄYLÄ:" in desc.upper() or "LIITÄNTÄ" in desc.upper():
						interface = desc
						
					elif "CACHE" in desc.upper() or "DRAM" in desc.upper():
						cache = desc
						
					elif "MUISTITYYPPI" in desc.upper() or "TALLENNUSMUISTI" in desc.upper() or "FLASH" in desc.upper():
						flash = desc
						
					elif "TBW" in desc.upper():
						tbw = desc
						
				elif "/fi/Product/List/000-00H" in get_category:
					part_type = "mobo"
					
					if "PIIRISARJATYYPPI" in desc.upper() or chipset_list is not None:
						if chipset_list is not None:
							chipset = chipset_list
						else:
							chipset = desc

					elif "TUOTTEEN TYYPPI" in desc.upper() or ff_list is not None:
						if ff_list is not None:
							form_factor = ff_list
						else:
							form_factor = desc

					elif "DDR" in desc.upper() and not "ADDRESS" in desc.upper() or mobo_memory_list is not None:
						if mobo_memory_list is not None:
							memory_compatibility = mobo_memory_list
						else:
							memory_compatibility = desc
							

					
				elif "/fi/Product/List/000-00J" in get_category:
					part_type = "case"
					print("Case")

				elif "/fi/Product/List/000-00M" in get_category:
					part_type = "addin"
					print("Addin")


				elif "/fi/Product/List/000-00N" in get_category:
					part_type = "ram"
					print("RAM")

				elif "/fi/Product/List/000-00P" in get_category:
					part_type = "gpu"

					if "NÄYTÖNOHJAIN" in trimmed_name.upper():
						trimmed_name = trimmed_name.upper().strip("NÄYTÖNOHJAIN").strip().rstrip("-").strip().capitalize()
						
					if "CUDA" in desc.upper() or "STREAM-PROSESSORIT" in desc.upper():
						cores = desc

					elif "BOOST" in desc.upper() or "KELLOTAAJUUS" in desc.upper() and "MHZ" in desc.upper():
						clock = desc

					elif "MÄÄRÄ" in desc.upper():
						memory = desc

					elif "VÄYLÄ" in desc.upper() and not "MUISTIVÄYLÄ" in desc.upper():
						interface = desc

					elif "MITAT" in desc.upper() or "PITUUS" in desc.upper():
						size = desc

					elif "TDP" in desc.upper() or "VIRTALÄHTE" in desc.upper():
						tdp = desc



				elif "/fi/Product/List/000-00R" in get_category:
					part_type = "cpu"
					
					
				elif "/fi/Product/List/000-00U" in get_category:
					part_type = "psu"
					print("PSU")

				else:
					print("Something went wrong. Category:", get_category)
					
			part_lists_dict = {
				"storage_list": [trimmed_name, capacity, form_factor, interface ,cache ,flash, tbw],
				"mobo_list": [chipset, form_factor, memory_compatibility],
				"gpu_list": [cores, clock, memory, interface, size, tdp],
				"cpu_list": [core_count, thread_count, base_clock, l3_cache, socket, cpu_cooler, tdp, igpu],
			}

			if part_type == "storage":
				item_list = part_lists_dict["storage_list"]
			elif part_type == "mobo":
				item_list = part_lists_dict["mobo_list"]
			elif part_type == "gpu":
				item_list = part_lists_dict["gpu_list"]
			elif part_type == "cpu":
				item_list = part_lists_dict["cpu_list"]
				
			item_list = trim_list(item_list)

			if part_type == "gpu" and item_list[5] and item_list[5] != None:
				if "VÄHINTÄÄN" in item_list[5].upper():
					item_list[5] = item_list[5].upper().strip("VÄHINTÄÄN")

			## Create dictionaries for all parts, like this
			if part_type == "storage":
				storage_dict = {
					"URL": curr_link,
					"Price": m_price,
					"Name": trimmed_name,
					"Manufacturer": m_manufacturer,
					"Capacity": item_list[0],
					"Form factor": item_list[1],
					"Interface": item_list[2],
					"Cache": item_list[3],
					"Flash": item_list[4],
					"TBW": item_list[5],
				}
				
			elif part_type == "mobo":
				motherboard_dict = {
					"URL": curr_link,
					"Price": m_price,
					"Name": trimmed_name,
					"Manufacturer": m_manufacturer,
					"Chipset": item_list[0],
					"Form factor": item_list[1],
					"Memory compatibility": item_list[2],
				}
				
			elif part_type == "gpu":
				gpu_dict = {
					"URL": curr_link,
					"Price": m_price,
					"Name": trimmed_name,
					"Manufacturer": m_manufacturer,
					"Cores": item_list[0],
					"Core Clock": item_list[1],
					"Memory": item_list[2],
					"Interface": item_list[3],
					"Size": item_list[4],
					"TDP": item_list[5],
				}
				
			elif part_type == "cpu":
				cpu_dict = {
					"URL": curr_link,
					"Price": m_price,
					"Name": trimmed_name,
					"Manufacturer": m_manufacturer,
					"Core Count": item_list[0],
					"Thread Count": item_list[1],
					"Base Clock": item_list[2],
					"L3 Cache": item_list[3],
					"Socket": item_list[4],
					"Cpu Cooler": item_list[5],
					"TDP": item_list[6],
					"Integrated GPU": item_list[7],
				}
			

					
			## Do the insertion of data to the database		

			#pprint(gpu_dict)
			#print("\n")


main()