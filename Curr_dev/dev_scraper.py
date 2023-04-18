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

		# Get motherboard chipset
		chipset_data = results_item.select_one("strong:-soup-contains('Piirisarja')")
		print("chipset_data:", chipset_data)
		next_to_chipset = chipset_data.find_next("strong")
		print("next_to_chipset:", next_to_chipset)
		
		if chipset_data and next_to_chipset and chipset_data is not None:
			siblings = chipset_data.find_next_siblings(string = True)
			print("siblings:", siblings)
			chipset_list = []
			for sibling in siblings:
				if sibling == next_to_chipset:
					break
				elif sibling.name in ["strong"]:
					break
				else:
					chipset_list.append(sibling.string.strip())
			print("\n\n\n\n", chipset_list)
						
					

		
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
				cores = None
				clock = None
				memory = None
				interface = None
				size = None
				tdp = None
				
				## Into these if statements, do as i've done in the gpu part already
				if "/fi/Product/List/000-00K" in get_category:
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
					if "EMOLEVYN TYYPPI" in desc.upper():
						pass
					
				elif "/fi/Product/List/000-00J" in get_category:
					print("Case")
				elif "/fi/Product/List/000-00M" in get_category:
					print("Addin")

				elif "/fi/Product/List/000-00N" in get_category:
					if "MUISTIT" in trimmed_name.upper():
						trimmed_name = trimmed_name.upper().strip("MUISTIT").strip().capitalize()
					
					if "KAPASITEETTI" in desc.upper():
						capacity = desc
					
					elif "NOPEUS" in desc.upper():
						speed = desc
					
					elif "LATENSSI:" in desc.upper():
						latency = desc
						
					elif "JÄNNITE" in desc.upper():
						voltage = desc
						
					elif "RANK" in desc.upper():
						rank = desc

				elif "/fi/Product/List/000-00P" in get_category:
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
					print("CPU")
				elif "/fi/Product/List/000-00U" in get_category:
					print("PSU")

				else:
					print("Something went wrong. Category:", get_category)
					
			gpu_list = [cores, clock, memory, interface, size, tdp]

			for i, item in enumerate(gpu_list):
				if item and item != None:
					data = item.split(":", 1)
					if len(data) > 1:
						gpu_list[i] = data[1].strip().capitalize()
					else:
						gpu_list[i] = item.strip().capitalize()

			if gpu_list[5] and gpu_list[5] != None:
				if "VÄHINTÄÄN" in gpu_list[5].upper():
					gpu_list[5] = gpu_list[5].upper().strip("VÄHINTÄÄN")


			## Create dictionaries for all parts, like this	
			memory_dict = {
				"Capacity": capacity,
				"Speed": speed,
				"Latency": latency,
				"Voltage": voltage,
				"Rank": rank,
			}

			storage_dict = {
				"Capacity": capacity,
				"Form factor": form_factor,
				"Interface": interface,
				"Cache": cache,
				"Flash": flash,
				"TBW": tbw,
			}
			
			gpu_dict = {
				"URL": curr_link,
				"Price": m_price,
				"Name": trimmed_name,
				"Manufacturer": m_manufacturer,
				"Cores": gpu_list[0],
				"Core Clock": gpu_list[1],
				"Memory": gpu_list[2],
				"Interface": gpu_list[3],
				"Size": gpu_list[4],
				"TDP": gpu_list[5],
			}
			

					
			## Do the insertion of data to the database		

			#pprint(gpu_dict)
			#print("\n")


main()