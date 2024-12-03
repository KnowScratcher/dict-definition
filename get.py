import requests
import bs4
import re
from definition import *

class Void:
    def __getattribute__(self, name):
        return None

pos = {"Noun","Verb","Pronoun","Adjective","Adverb","Preposition","Conjunction","Interjection","Determiner","Article"}

wiki_url = "https://en.m.wiktionary.org/wiki/"
unused_tag = re.compile("<sup.*?sup>|<[^\/ibp].*?>|<\/[^ibp].*?>")
class Finder:
    def __init__(self,word:str) -> None:
        self.word:str = word
        self.page = requests.get(wiki_url + word)
        self.soup = bs4.BeautifulSoup(self.page.text,"html5lib")
        self.section:bs4.NavigableString = bs4.BeautifulSoup(str(self.soup.find(id="English").parent.find_next("section")),"html5lib")
    
        self.word_class = Word(self.word,[],[])

        self.find_pronunciation()
        self.find_etymologies()
    def find_etymologies(self) -> None:
        try: # single
            build = ""
            etymology = self.section.find(id="Etymology").parent.find_next("p")
            while etymology.name == "p":
                build += str(etymology)
                etymology = etymology.find_next_sibling()
            self.word_class.etymologies = [Etymology(re.sub(unused_tag,"",str(build)),self.find_pos_single())]
            return
        except: # multiple
            try:
                build = []
                
                index = 1
                while True:
                    etymology = self.section.find(id=f"Etymology_{index}").parent.find_next("p")
                    build_text = "" # build the etymology html text
                    while etymology.name == "p":
                        build_text += str(etymology)
                        etymology = etymology.find_next_sibling()
                    build.append(Etymology(re.sub(unused_tag,"",str(build_text)),self.find_pos_multiple(self.section.find(id=f"Etymology_{index}"))))
                    index += 1
            except:
                self.word_class.etymologies = build
                return

    def find_pronunciation(self) -> None:
        pronunciation_list = self.section.find(id="Pronunciation").parent.find_next("ul")
        pronunciation_element = pronunciation_list.find("li") # li
        ipas = set()
        while pronunciation_element is not None and pronunciation_element.name == "li":
            # print(pronunciation_element)
            ipa = pronunciation_element.find(class_="IPA")
            # print(0)
            if ipa is not None and ipa.parent.find(string="IPA") is not None:
                # print(1)
                key = pronunciation_element.find(class_="usage-label-accent")
                key = key.text if key is not None else "IPA"
                # print(key)
                ipas.add((key,ipa.text))
            pronunciation_element = pronunciation_element.find_next("li") # _sibling
            # print(ipas)
        self.word_class.pronunciation = list(ipas)
        return

    def find_pos_single(self) -> list[Pos]: # h3
        h3s = self.section.find_all("h3")
        build = []
        for i in filter(lambda x:x["id"] in pos,h3s):
            build.append(Pos(i["id"],definitions=self.find_definition_single(i)))
        return build


    def find_pos_multiple(self,anchor) -> list[Pos]: # h4
        pass

    def find_definition_single(self,pos,p=None) -> list[Definition]:
        if p is None:
            ol = pos.parent.find_next("ol")
            pointer = ol.find("li", recursive=False)
            layer = 1
        else:
            pointer = p
        build = []
        base_pointers = [] # (pointer,pointer.find(".usage-label-sense").text or "")
        while True:
            if pointer is None or pointer.name != "li":
                layer -= 1
                if not layer:
                    break
                pointer = base_pointers[-1][0].find_next_sibling()
                base_pointers.pop()
                continue
            if len(pointer.findChildren("ol", recursive=False)) > 0:
                layer += 1
                base_pointers.append((pointer,(pointer.find("span",_class="usage-label-sense") or Void()).text or None))
                pointer = pointer.findChildren("ol", recursive=False)[0].find("li")
                continue

            if (pointer.has_attr("class") and "empty" in pointer["class"][0]):
                pointer = pointer.find_next_sibling()
                continue
            def_string_build = []
            quote_string_build = []
            for i in pointer.contents:
                match i:
                    case str(i):
                        def_string_build.append(str(i))
                    case tag if str(tag).startswith("<dl>"): # syn, ant...
                        pass
                    case tag if str(tag).startswith("<ul>"): # quotation
                        pass
                    case i:
                        def_string_build.append(i.get_text())
                    
            build.append(Definition("".join(def_string_build),[],[],[],[]))
            pointer = pointer.find_next_sibling()
        print(len(build))
        return build

finder = Finder("cathead")
print(finder.word_class)


