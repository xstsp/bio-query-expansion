import logging

from flask import Flask

from api.controllers import api

app = Flask(__name__)

# Load configuration from config file.
# app.config.from_object('api.config')

# Register Flask modules.
app.register_blueprint(api)

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
