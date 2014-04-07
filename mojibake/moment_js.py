#Credit to
#http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-dates-and-times

from jinja2 import Markup

class moment_js:

    def __init__(self, timestamp):
        self.timestamp = timestamp

    def __call__(self, *args):
        return self.format(*args)

    def render(self, format):
        return Markup('<script>\ndocument.write(moment("{}").{});\n</script>'.format(self.timestamp.strftime('%Y-%m-%dT%H:%M:%S Z'), format))

    def format(self, fmt):
        return self.render('format("{}")'.format(fmt))

    def calendar(self):
        return self.render('calendar()')

    def fromNow(self):
        return self.render('fromNow()')
