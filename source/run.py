# -*- coding: utf-8 -*-

"""
Main module to run application.
"""

# Standard libraries import
import logging
import sys

# Append source path on wsgi initialization
sys.path.append('source')

# Application moudles import
from blueprints import application
from models import database
from config import CONFIG
from identica import IdenticaManager

@application.cli.command('run-identica')
def run_identica():
	"""
	Run IdenticaManager to communicate with Identica Bot.
	"""
	IdenticaManager(debug_mode=True).run()


# Run application on executing module
if __name__ == '__main__':
	application.run(
		CONFIG['web']['host'], CONFIG['web']['port'],
		threaded=True
	)
