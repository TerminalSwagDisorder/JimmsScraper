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


def main():
	# Urls for jimms
	URL = "https://www.jimms.fi"
	base_URL = "/fi/Product/Show/"
	component_URL = ["/fi/Product/List/000-00K/komponentit--kiintolevyt-ssd-levyt", "/fi/Product/List/000-00H/komponentit--emolevyt", "/fi/Product/List/000-00J/komponentit--kotelot", "/fi/Product/List/000-00M/komponentit--lisakortit", "/fi/Product/List/000-00N/komponentit--muistit", "/fi/Product/List/000-00P/komponentit--naytonohjaimet", "/fi/Product/List/000-00R/komponentit--prosessorit", "/fi/Product/List/000-00U/komponentit--virtalahteet"]
	component_URL2 = ["/fi/Product/List/000-00H/komponentit--emolevyt", "/fi/Product/List/000-00K/komponentit--kiintolevyt-ssd-levyt", "/fi/Product/List/000-00J/komponentit--kotelot", "/fi/Product/List/000-00M/komponentit--lisakortit", "/fi/Product/List/000-00N/komponentit--muistit", "/fi/Product/List/000-00P/komponentit--naytonohjaimet", "/fi/Product/List/000-00R/komponentit--prosessorit", "/fi/Product/List/000-00U/komponentit--virtalahteet"]

	driver_path = "./chromedriver_win32/chromedriver.exe"

	driver = webdriver.Chrome(executable_path=driver_path)
	
	get_subpages(URL, component_URL, driver)



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
			

			
def get_subpages(URL, component_URL, driver):
	#Get subpages for all components
	for item in component_URL:		
		subpage = "?p="
		
		listz = [1]

		print("Getting all pages for", item)
		
		# Go to page using Selenium
		driver.get(URL + item + "?p=1")
		wait = WebDriverWait(driver, 10)
		button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@data-bind='click: moveToLastPage']")))
		driver.execute_script("arguments[0].scrollIntoView();", button)
		driver.execute_script("arguments[0].click();", button)
		sleep(2)
		
		# Get the URL
		last_page_url = driver.current_url
		last_page_number = int(last_page_url.split("=")[-1])
		listz.append(last_page_number)
		
		# Add subpage numbers to listz
		page_nums = range(listz[0] + 1, listz[1])
		for num in page_nums:
			listz.append(num)
			listz.sort()
		
		# Create a new list with added parameter
		pages = [str(i) for i in listz]
		pages_with_param = [subpage + page for page in pages]		
		print(pages_with_param)
		sleep(2)
	driver.close()
	driver.quit()


			

main()