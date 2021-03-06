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
import blueprints
from config import CONFIG
from models import database
from identica import IdenticaManager
from blueprints.__permission__ import configure_permissions

application = blueprints.application
socketio = blueprints.socketio


@application.cli.command('run-identica')
def run_identica():
	"""
	Run IdenticaManager to communicate with Identica Bot.
	"""
	IdenticaManager().run()


@application.cli.command('run-socketio')
def run_socketio():
	"""
	Run SocketIO server.
	"""
	socketio.run(
		application,
		host=CONFIG['web']['host'],
		port=CONFIG['web']['port']
	)


@application.cli.command('run-permissions')
def run_permissions():
	"""
	Run permissions configure.
	"""
	configure_permissions()


# Run application on executing module
if __name__ == '__main__':
##	application.run(threaded=True)
	socketio.run(
		application,
		host=CONFIG['web']['host'],
		port=CONFIG['web']['port']
	)
