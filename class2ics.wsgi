#! /usr/bin/python3.6

import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/var/www/class2ics')
from server import app as application
application.secret_key = 'just_a_secret_key'

