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
	component_URL = ["/fi/Product/List/000-00P/komponentit--naytonohjaimet"]
	component_URL2 = ["https://www.jimms.fi/fi/Product/Show/187728/tuf-rtx4070ti-o12g-gaming/asus-geforce-rtx-4070-ti-tuf-gaming-oc-edition-naytonohjain-12gb-gddr6x-asus-cashback-70"]
	component_temp = ["/fi/Product/List/000-00K/komponentit--kiintolevyt-ssd-levyt", "/fi/Product/List/000-00H/komponentit--emolevyt", "/fi/Product/List/000-00J/komponentit--kotelot", "/fi/Product/List/000-00M/komponentit--lisakortit", "/fi/Product/List/000-00N/komponentit--muistit", "/fi/Product/List/000-00P/komponentit--naytonohjaimet", "/fi/Product/List/000-00R/komponentit--prosessorit", "/fi/Product/List/000-00U/komponentit--virtalahteet"]

	driver_path = "./chromedriver_win32/chromedriver.exe"

	driver = webdriver.Chrome(executable_path=driver_path)
	
	index_pages_dict = get_subpages(base_URL, component_URL, driver)
	all_product_links = get_urls(base_URL, index_pages_dict)
	data_scraper(base_URL, all_product_links)

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
	
	#Get subpages for all components
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
					if "Tarjous" not in item.text and "Bundle" not in item.text:
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
		
		# Get the data and trim it
		results_item = item_soup.find("div", itemprop="description")
		data_start = results_item.find_all(["p", "ul", "li"])
		
		print(curr_link)
		desc_data = results_item.find("strong", text="Tekniset tiedot")
		if desc_data is not None:
			trimmed_data = desc_data.find_all_next(recursive = False)
			list_list = []
			for item in trimmed_data:
				if item.name in ["div", "a"]:
					print("break:", item.name)
					break
				elif item.name in ["li", "ul"]:
					list_item = item.text.strip("\n")
					if list_item and list_item not in list_list:
						print(list_item)
						list_list.append(list_item)
					#print(list_list)
					#print(item.text)
						
		#splitlines()	#Splits the string at line breaks and returns a list

		if "/fi/Product/List/000-00K" in get_category:
			print("Drive")
		elif "/fi/Product/List/000-00H" in get_category:
			print("Mobo")
		elif "/fi/Product/List/000-00J" in get_category:
			print("Case")
		elif "/fi/Product/List/000-00M" in get_category:
			print("Addin")
		elif "/fi/Product/List/000-00N" in get_category:
			print("RAM")
		elif "/fi/Product/List/000-00P" in get_category:
			gpu_dict = {
			"Color": None,
			"Memory": None,
			"Memory Type": None,
			"Core Clock": None,
			"Boost Clock": None,
			"Effective Memory Clock": None,
			"Interface": None,
			"TDP": None,
			"Cooling": None,
			}
		elif "/fi/Product/List/000-00R" in get_category:
			print("CPU")
		elif "/fi/Product/List/000-00U" in get_category:
			print("PSU")
			
		else:
			print("Something went wrong. Category:", get_category)
		
		
		sleep(0.2)
		#print(desc_data)

main()