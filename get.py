import requests
import bs4
import re
from definition import *


wiki_url = "https://en.m.wiktionary.org/wiki/"
unused_tag = re.compile("<sup.*?sup>|<[^\/ibp].*?>|<\/[^ibp].*?>")
class Finder:
    def __init__(self,word:str) -> None:
        self.word:str = word
        self.page = requests.get(wiki_url + word)
        self.soup = bs4.BeautifulSoup(self.page.text,"html5lib")

        self.section:bs4.NavigableString = self.soup.find(id="English").parent.find_next("section")
    
        self.word_class = Word(self.word,[],[])

        self.find_pronunciation()
        self.find_etymologies()
    def find_etymologies(self) -> list[Etymology]:
        try:
            build = ""
            etymology = self.section.find(id="Etymology").parent.find_next("p")
            while etymology.name == "p":
                build += str(etymology)
                etymology = etymology.find_next_sibling()
            self.word_class.etymologies = [Etymology(re.sub(unused_tag,"",str(build)),[])]
            return
        except:
            try:
                build = []
                
                index = 1
                while True:
                    etymology = self.section.find(id=f"Etymology_{index}").parent.find_next("p")
                    build_text = "" # build the etymology html text
                    while etymology.name == "p":
                        build_text += str(etymology)
                        etymology = etymology.find_next_sibling()
                    build.append(Etymology(re.sub(unused_tag,"",str(build_text)),[]))
                    index += 1
            except:
                self.word_class.etymologies = build
                return

    def find_pronunciation(self) -> None:
        pronunciation_list = self.section.find(id="Pronunciation").parent.find_next("ul")
        pronunciation_element = pronunciation_list.find("li") # li
        ipas = []
        try:
            while pronunciation_element.name == "li":
                # print(pronunciation_element)
                ipa = pronunciation_element.find(class_="IPA")
                # print(0)
                if ipa is not None and ipa.parent.find(string="IPA") is not None:
                    # print(1)
                    key = pronunciation_element.find(class_="extiw")
                    key = key.text if key is not None else "IPA"
                    # print(key)
                    ipas.append((key,ipa.text))
                pronunciation_element = pronunciation_element.find_next_sibling()
                # print(ipas)
        except:
            pass
        self.word_class.pronunciation = ipas
        return


finder = Finder("cathead")
print(finder.word_class)


