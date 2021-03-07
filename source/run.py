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
from models import database
from identica import IdenticaManager

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
	socketio.run(application)


# Run application on executing module
if __name__ == '__main__':
#	application.run(threaded=True)
	socketio.run(application)
