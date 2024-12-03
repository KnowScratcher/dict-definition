from dataclasses import dataclass
from typing import Literal, Any


class Jsonable:
    def __repr__(self) -> str:
        return str(self.__dict__)

@dataclass(repr=False)
class Quote(Jsonable):
    citation:str | None = None
    textHTML:str | None = None
    # time:str | None = None

@dataclass(repr=False)
class Definition(Jsonable):
    definition:str
    quote:list[Quote]
    derivedTerm:list[str]
    synonyms:list[str]
    antonyms:list[str]

@dataclass(repr=False)
class Pos(Jsonable):
    pos:str | Literal["Noun","Verb","Pronoun","Adjective","Adverb","Preposition","Conjunction","Interjection","Determiner","Article"]
    definitions:list[Definition]


@dataclass(repr=False)
class Etymology(Jsonable):
    etymologyHTML:str
    pos:list[Pos]

@dataclass(repr=False)
class Word(Jsonable):
    text:str
    etymologies:list[Etymology]
    pronunciation:list[tuple[str,str]] # list of tuple = (key,ipa), key = region or pos
