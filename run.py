#!/usr/bin/env python

from mojibake.main import app
from mojibake.settings import DEBUG

if __name__ == '__main__':

    app.logger.debug('Begin Mojibake DEBUG={}'.format(DEBUG))

    app.run(debug=DEBUG)
