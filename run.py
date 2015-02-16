import logging

from mojibake.main import app
from mojibake.settings import DEBUG

logger = logging.getLogger('mojibake')
formatter = logging.Formatter('%(asctime)s [%(levelname)s] - %(message)s')
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
if DEBUG:
    handler.setLevel(logging.DEBUG)
else:
    handler.setLevel(logging.INFO)

logger.addHandler(handler)
if DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

app.run(debug=DEBUG)
