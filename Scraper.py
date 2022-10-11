#https://realpython.com/beautiful-soup-web-scraper-python/

import requests
from bs4 import BeautifulSoup

URL = "https://www.jimms.fi"
base_URL = "/fi/Product/Show/"
component_URL = ["/fi/Product/List/000-00H/komponentit--emolevyt"]
component_URL2 = ["/fi/Product/List/000-00K/komponentit--kiintolevyt-ssd-levyt", "/fi/Product/List/000-00J/komponentit--kotelot", "/fi/Product/List/000-00M/komponentit--lisakortit", "https://www.jimms.fi/fi/Product/List/000-00N/komponentit--muistit", "/fi/Product/List/000-00P/komponentit--naytonohjaimet", "/fi/Product/List/000-00R/komponentit--prosessorit", "/fi/Product/List/000-00U/komponentit--virtalahteet"]

for item in component_URL:
    page = requests.get(URL + item, allow_redirects=True)
    soup = BeautifulSoup(page.content, "html.parser")
    try:
        results = soup.find("div", class_="p_name").find_all("a")
    except:
        pass
    listx = []
    for x in soup.find_all('a', href=True):
        listx.append(x["href"]) 
        listy = [x for x in listx if x.startswith(base_URL)]
        listy = list(dict.fromkeys(listy))
    print(listy)
    
    for y in listy:
        item_Page = requests.get(URL + y, allow_redirects=True)
        Item_soup = BeautifulSoup(item_Page.content, "html.parser")
        print(item_Page.url, item_Page.history)


        results_Item = Item_soup.find("div", itemprop="description").find("p")
        stripchars = results_Item.text.split("Tekniset tiedot:", 1)
        if len(stripchars) > 0:
            try:
                results_Item = stripchars[1]
            except:
                pass
        print(results_Item)
        



#print(results)
'''
stripchars = results.text.split("Tekniset tiedot:", 1)
if len(stripchars) > 0:
    results = stripchars[1]
print(results)
'''
#print(page.text)

