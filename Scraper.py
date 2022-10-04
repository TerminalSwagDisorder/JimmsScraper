#https://realpython.com/beautiful-soup-web-scraper-python/

import requests
from bs4 import BeautifulSoup

baseurl = "/fi/Product/Show/"
URL = "https://www.jimms.fi/fi/Product/List/000-00P/komponentit--naytonohjaimet"
#URL = "https://www.jimms.fi/fi/Product/Show/173495/tuf-rtx3080-o10g-v2-gaming/asus-geforce-rtx-3080-tuf-gaming-oc-edition-lhr-naytonohjain-10gb-gddr6x"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")
results = soup.find("div", class_="p_name").find_all("a")
#results = soup.find("div", itemprop="description").find("p")
listx = []
for x in soup.find_all('a', href=True):
    listx.append(x["href"])
    listy = [x for x in listx if x.startswith(baseurl)]
print(listy)


        
#print(results)
'''
stripchars = results.text.split("Tekniset tiedot:", 1)
if len(stripchars) > 0:
    results = stripchars[1]
print(results)
'''
#print(page.text)

