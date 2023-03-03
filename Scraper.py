#https://realpython.com/beautiful-soup-web-scraper-python/

import requests
from bs4 import BeautifulSoup

URL = "https://www.jimms.fi"
base_URL = "/fi/Product/Show/"
component_URL = ["/fi/Product/List/000-00K/komponentit--kiintolevyt-ssd-levyt"]
component_URL2 = ["/fi/Product/List/000-00H/komponentit--emolevyt", "/fi/Product/List/000-00K/komponentit--kiintolevyt-ssd-levyt", "/fi/Product/List/000-00J/komponentit--kotelot", "/fi/Product/List/000-00M/komponentit--lisakortit", "https://www.jimms.fi/fi/Product/List/000-00N/komponentit--muistit", "/fi/Product/List/000-00P/komponentit--naytonohjaimet", "/fi/Product/List/000-00R/komponentit--prosessorit", "/fi/Product/List/000-00U/komponentit--virtalahteet"]
def main():
	for item in component_URL:
		#page = requests.get(URL + item, allow_redirects=True)
		#soup = BeautifulSoup(page.content, "html.parser")

		#Get next page URLs
		listz = ["?p=1"]
		print("Getting all pages for", item)
		i = 1
		for z in listz:
			next_Page = requests.get(URL + item + z)
			next_Soup = BeautifulSoup(next_Page.content, "html.parser")
			page_Cont = next_Soup.find("div", id="productlist")
			list_Element = page_Cont.find_all("li", class_="page-item", attrs={"data-bind":"css: { disabled: page() === lastPage() }"})
			nav_Element = next_Soup.find("nav", attrs={'aria-label': 'Listauksen sivu'})

			try:
				page_Item = nav_Element.find("li", class_="page-item", attrs={"data-bind":"css: { active: $data.pageNumber === ($parent.selectedPage()) }"})
				#print("page_Item", page_Item)
				page_Link = page_Item.find("a")
				page_Link_element = element.get("data-bind")
				text_value = eval(page_Link_element)['text']
				print(text_value)
				curr_Page = page_Link["href"]
				listz.append(curr_Page)
				
			except:
				break




			#next_Results = next_Soup.find("div", id="productlist").find_all("a", class_="page-link", attrs={"data-bind": "click: moveToNextPage"})


			#print(next_Page.url)
			#results = next_Soup.find("div", class_="p_name").find_all("a")

					

			# Get the links to all the components on all pages
			
		for z in listz:
			page = requests.get(URL + item + z)
			soup = BeautifulSoup(page.content, "html.parser")
			
			try:
				results = soup.find("div", class_="p_name").find_all("a")
			except:
				print("There are no more links")
				continue
				
			#print("results:", results)
			listx = []
			for x in soup.find_all("a", href=True):
				listx.append(x["href"]) 
				listy = [x for x in listx if x.startswith(base_URL)]
				listy = list(dict.fromkeys(listy))
				
			print("listy:", listy)
			print("current page:", page.url)


		# Get the text in the item pages
			for y in listy:
				item_Page = requests.get(URL + y, allow_redirects=True)
				item_Soup = BeautifulSoup(item_Page.content, "html.parser")
				#print("item url:", item_Page.url, item_Page.history)

				print(item_Page)
				results_Item = item_Soup.find("div", itemprop="description")
				producer_Name = item_Soup.find("div", class_="nameinfo").find("h1").find("span", itemprop="brand").find("span", itemprop="name").text
				item_Name = item_Soup.find("div", class_="nameinfo").find("h1", class_="name").find_all("span")[2].text
				item_Name2 = item_Name.split(",", 1)
				item_Smallspecs = item_Soup.find("div", class_="nameinfo").find("p")
				
				if item_Smallspecs is None:
					item_Smallspecs = None
				else:
					item_Smallspecs = item_Soup.find("div", class_="nameinfo").find("p").text
					
				item_Price = item_Soup.find("span", class_="pricetext").find("span", itemprop="price").text
				item_Price = float(item_Price.replace(" ", "").replace(",", ".").lstrip())
				
				try:
					stripchars = results_Item.text.split("Tekniset tiedot:", 1)
				except:
					print("There was an exception with the item page")
					continue
					
				if len(stripchars) > 0:
					try:
						results_Item = stripchars[1]
					except:
						print("The text could not be handled")
						continue
											
				if len(item_Name2) > 1:
					print("Manufacturer Name:", producer_Name, "\nItem name:", item_Name2[0], "\nItem type:", item_Name2[1], "\nItem smallspecs:", item_Smallspecs, "\nPrice:", item_Price)
				else:
					print("Manufacturer Name:", producer_Name, "\nItem name:", item_Name2[0], "\nItem type:", None, "\nItem smallspecs:", item_Smallspecs, "\nPrice:", item_Price)
				#print(results_Item)
main()



#print(results)
'''
stripchars = results.text.split("Tekniset tiedot:", 1)
if len(stripchars) > 0:
	results = stripchars[1]
print(results)
'''
#print(page.text)

