import requests
import bs4
page = requests.get("https://en.m.wiktionary.org/wiki/elaborate")
soup = bs4.BeautifulSoup(page.text,"html5lib")

section = soup.find(id="English").parent.find_next("section").prettify()
print(section)