import json
from definition import *

w = Word("lol", [Etymology("<p>lol</p>",[Definition("eruiirhwui",[Quote("<p>test</p>","tedff","time")],["streee"],["syn"],["ant"])])],[("US","lol")])
# print(eval(repr(w)))
with open("definitions\\test.json","w",encoding="UTF-8") as f:
    json.dump(eval(repr(w)),f,indent="\t")