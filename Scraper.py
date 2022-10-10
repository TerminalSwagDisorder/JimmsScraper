#https://realpython.com/beautiful-soup-web-scraper-python/

import requests
from bs4 import BeautifulSoup

URL = "https://www.jimms.fi"
Base_URL = "/fi/Product/Show/"
Component_URL = ["/fi/Product/List/000-00H/komponentit--emolevyt"]
Component_URL2 = ["/fi/Product/List/000-00K/komponentit--kiintolevyt-ssd-levyt", "/fi/Product/List/000-00J/komponentit--kotelot", "/fi/Product/List/000-00M/komponentit--lisakortit", "https://www.jimms.fi/fi/Product/List/000-00N/komponentit--muistit", "/fi/Product/List/000-00P/komponentit--naytonohjaimet", "/fi/Product/List/000-00R/komponentit--prosessorit", "/fi/Product/List/000-00U/komponentit--virtalahteet"]

for item in Component_URL:
    page = requests.get(URL + item, allow_redirects=True)
    soup = BeautifulSoup(page.content, "html.parser")
    try:
        results = soup.find("div", class_="p_name").find_all("a")
    except:
        pass
    listx = []
    for x in soup.find_all('a', href=True):
        listx.append(x["href"]) 
        listy = [x for x in listx if x.startswith(Base_URL)]
        listy = list(dict.fromkeys(listy))
    print(listy)
    
    for y in listy:
        Item_page = requests.get(URL + y, allow_redirects=True)
        Item_soup = BeautifulSoup(Item_page.content, "html.parser")
        print(Item_page.url, Item_page.history)


        results_item = Item_soup.find("div", itemprop="description").find("p")
        stripchars = results_item.text.split("Tekniset tiedot:", 1)
        if len(stripchars) > 0:
            try:
                results_item = stripchars[1]
            except:
                pass
        print(results_item)


        

#print(results)
'''
stripchars = results.text.split("Tekniset tiedot:", 1)
if len(stripchars) > 0:
    results = stripchars[1]
print(results)
'''
#print(page.text)

