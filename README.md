MØjibДĸe
================================

The early stages of a blog engine!
Written in Python 3 and Flask.

Currently in the process of re-writing this.

TO DO
-------------------------
- Currently all times added are assumed UTC
- Add a Tag and Category slug? Okay with spaces in the url?
- Add a preview view for writing posts?
- Add search
- ~~For narrow view settings, move the tags under the post date~~ This should be okay now I've removed the author name
- Do similar for category, except under the title?
- Look at Disqus for comments?

REQUIREMENTS
-------------------------

Python

See requirements.txt

MISC
-------------------------

### PyBabel Commands ###
    pybabel extract -F babel.cfg -o messages.pot mojibake

Then use [Poedit](http://poedit.net/) to update the translation from the .pot file, or do it from the command line;

To create the translations

    pybabel init -i messages.pot -d mojibake/translations -l ja

To update the translations with new text from messages.pot

    pybabel update -i messages.pot -d mojibake/translations

To use the translations once translated or pulled down from Git

    pybabel compile -d mojibake/translations
