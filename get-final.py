import requests
import bs4
import re
from definition import *
import json
import dataclasses
from tqdm import tqdm
import os

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
        i = anchor
        build = []
        section = []
        k = i.parent.find_next_sibling()
        while k!=None and (not k.has_attr("class") or ("mw-heading3" not in k["class"])):
            section.append(str(k))
            k = k.find_next_sibling()
            
        section = "".join(section)
        s = bs4.BeautifulSoup(section,"html5lib")
        h4s = s.find_all("h4")
        for j in filter(lambda x: any(p in x["id"] for p in pos),h4s):
            build.append(Pos(j["id"].split("_")[0],definitions=self.find_definition_single(j)))
        return build

    def find_definition_single(self,pos=None,skip=False,prefix="") -> list[Definition]:
        full = []
        build = []
        build_quote = []
        build_relative = {}
        if not skip:
            pointer = pos.parent.find_next("ol")
        else:
            pointer = pos
        for i in pointer.contents:
            if str(i) == '<li class="mw-empty-elt"></li>':
                continue
            elif str(i).startswith("<li") or str(i).startswith("<ol"):
                full.extend(self.find_definition_single(i,True))
            elif str(i).startswith("<ul"):
                build_quote.extend(self.find_quote(i))
            elif str(i).startswith("<dl"):
                build_relative = self.find_sact(i)
            elif skip: # if it's inside
                build.append(i.get_text())
        if len(build) > 0 and not all(["\n" == i for i in build]):
            full.append(Definition(definition="".join(build),quote=build_quote,relative=build_relative))
        # print(len(full))
        return full
    
    def find_quote(self,pointer) -> list[Quote]:
        build_cite = []
        build_text = []
        full = []
        for i in pointer.contents:
            if str(i) == '<li class="mw-empty-elt"></li>':
                continue
            elif str(i).startswith("<li") or str(i).startswith("<div"):
                full.extend(self.find_quote(i))
            elif str(i).startswith("<dl"):
                build_text.append(i.get_text())
            else: # if it's inside
                build_cite.append(i.get_text())
        if len(build_cite) > 0 and len(build_text) > 0:
            full.append(Quote(citation="".join(build_cite),text="".join(build_text)))
        return full
    
    def find_sact(self,pointer) -> dict[str,list[str]]: # synonym, antonym, derived term
        build = {}
        for i in pointer.contents:
            if str(i).startswith("<dd"):
                text = str(i.get_text()).split(":")
                if len(text) == 2:
                    build[text[0]] = [s.strip() for s in re.split('; |, ', text[1])]
        return build
    
class EnhancedJSONEncoder(json.JSONEncoder):
            def default(self, o):
                if dataclasses.is_dataclass(o):
                    return dataclasses.asdict(o)
                return super().default(o)
            
# main script
with open("7000.txt") as d:
    word_list = d.readlines()
for i in tqdm(word_list):
    i = i.strip()
    if os.path.exists(f"./out/{i}.json"):
        print(f"\nskipped {i} because it exists in the database")
    else:
        try:
            
            finder = Finder(i)
        except:
            print(f"\nfailed to fetch {i}")
        else:
            try:
                with open(f"./out/{i}.json","w",encoding="UTF-8") as o:
                    json.dump(finder.word_class,o,cls=EnhancedJSONEncoder)
            except:
                print(f"\nfailed to write to {i}.json")



