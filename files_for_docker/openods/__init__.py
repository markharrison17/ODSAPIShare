__version__ = '0.16'

import logging.handlers
import re

# Import flask
from flask import Flask
from flask_cors import CORS
from flask_featureflags import FeatureFlag

# Define the WSGI application object
app = Flask(__name__)
feature_flags = FeatureFlag(app)

# Load the app configuration from the default_config.py file
app.config.from_object('openods.default_config')

from openods import connection


import openods.handlers.handlers
import openods.handlers.ord_organisations_handler
import openods.handlers.ord_ods_code_handler
import openods.handlers.ord_sync_handler
import openods.handlers.fhir_ods_code_handler
import openods.handlers.fhir_organisations_handler
import openods.handlers.fhir_capabilities_handler
import openods.handlers.fhir_roles_handler
import openods.handlers.upload_file_handler
import openods.handlers.kill_thread_handler

# Set up logging - to stdout and disk by default
log_format = "%(asctime)s|OpenODS|%(levelname)s|%(message)s"
formatter = logging.Formatter(log_format)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG) #if app.config["DEBUG"] is True else logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

fh = logging.handlers.RotatingFileHandler(app.config['LOG_FILENAME'], maxBytes=app.config['LOG_MAXSIZE'],
                                          backupCount=app.config['LOG_BACKUP_NUM'])
fh.setFormatter(formatter)
logger.addHandler(fh)

logger.debug("Logging at DEBUG level")

# Allow Cross Origin Resource Sharing for routes under the API path so that other services can use the API
regEx = re.compile(app.config['API_PATH'] + "/*")
CORS(app, resources={regEx: {"origins": "*"}})



