import sys
import os
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'zpsbAPI')))
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
