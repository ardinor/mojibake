MØjibДĸe
================================

The early stages of a blog engine!
Written in Flask.

Currently in the process of re-writing this.


REQUIREMENTS
-------------------------

Python

See requirements.txt


pybabel extract -F babel.cfg -o messages.pot mojibake
pybabel update -i messages.pot -d mojibake/translations
pybabel compile -d mojibake/translations
