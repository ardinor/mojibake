from mojibake.main import app
from mojibake.settings import DEBUG

app.logging.debug('Begin Mojibake DEBUG={}'.format(DEBUG))

app.run(debug=DEBUG)
