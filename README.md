MØjibДĸe
================================

The early stages of a blog engine!
Written in Python 3 and Flask.

Currently in the process of re-writing this.

TO DO
-------------------------
- Add a Tag and Category slug? Okay with spaces in the url?
- Add a preview view for writing posts?

REQUIREMENTS
-------------------------

Python

See requirements.txt

MISC
-------------------------

### PyBabel Commands ###
pybabel extract -F babel.cfg -o messages.pot mojibake

pybabel init -i messages.pot -d mojibake/translations -l ja
 or
pybabel update -i messages.pot -d mojibake/translations

~~pybabel compile -d mojibake/translations~~
