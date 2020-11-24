#!/usr/bin/python

import glob
import json
import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

CWD = Path(os.path.dirname(__file__))

env = Environment(loader=FileSystemLoader(CWD / "files/templates"))
tmp = env.get_template("README.jinja.md")

langs = dict()
for filename in glob.glob(str(CWD / "files/readme/*.json")):
    lang = os.path.splitext(os.path.basename(filename))[0]
    with open(filename) as f:
        langs[lang] = json.loads(f.read())

print(langs)
for lang in langs.keys():
    with open(CWD / ("../README." + lang + ".md"), "w") as f:
        f.write(tmp.render(langs[lang]))
