﻿MØjibДĸe
================================

The early stages of a blog engine!
Written in Python 3 and Flask.

Currently in the process of re-writing this.


REQUIREMENTS
-------------------------

Python

See requirements.txt


pybabel extract -F babel.cfg -o messages.pot mojibake

pybabel init -i messages.pot -d mojibake/translations -l ja
 or
pybabel update -i messages.pot -d mojibake/translations

~~pybabel compile -d mojibake/translations~~
