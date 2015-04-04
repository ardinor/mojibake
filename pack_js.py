import logging

from webassets import Environment
from webassets import Bundle
from webassets.script import CommandLineEnvironment

# Bundle and minify the javascript
# Since Flask isn't serving the JS this needs to be done here
# before the static files are pulled down on nginx
# Kind of not the way I was hoping to handle this

log = logging.getLogger('webassets')
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)

env = Environment('mojibake/static', '/static')
js = Bundle('js/jquery.min.js',
            'js/jquery-ui.custom.js',
            'js/skel.min.js',
            'js/skel-panels.min.js',
            'js/init.js',
            'js/mojibake.js',
            filters='jsmin',
            output='js/packed.js')
env.register('js_all', js)

# From the docs
# https://webassets.readthedocs.org/en/latest/script.html
cmdenv = CommandLineEnvironment(env, log)
cmdenv.build()
