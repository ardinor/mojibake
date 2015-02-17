MØjibДĸe
================================

The early stages of a blog engine!
Written in Python 3 and Flask.

Currently in the process of re-writing this.

TO DO
-------------------------
- If a post is deleted and then a tag or category has no other posts, delete that tag or category
- Check adding translations from post edit
- Add a Tag and Category slug? Okay with spaces in the url?
- Add a preview view for writing posts?
- Add search
- Do similar for category, except under the title?
- Look at Disqus for comments?
- Maybe make the links a little more visible?
- Logging - send it to stdout so it shows up in docker logs
- Remove all the logic out of monitoring/templates/views.py and into scrutiny (to be uploaded into the DB).
 - Look at paginating the results of monitoring, it's far too large to display on one page.

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
