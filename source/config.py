# -*- coding: utf-8 -*-

"""
Configuration module to define application variables and constants.
"""

# Standard libraries import
import os
import sys
import json
import logging
from enum import Enum

# Environment value keys
CONFIG_PATH_KEY = 'AVATAR_CONFIG_PATH'
LOCALE_PATH_KEY = 'AVATAR_LOCALE_PATH'

# Application constants
CONFIG_PATH = 'config/app.json'
LOCALE_PATH = 'source/locale.json'
STATIC_PATH = 'source/static'
TEMPLATE_PATH = 'source/templates'
DATABASE_PATH = 'database'
PLUGINS_PATH = 'source/plugins'
GIFS_PATH = 'source/gifs'


def define_from(environ_key: str, default_path: str) -> dict:
	"""
	Return dictionary from json-file
	defined by environment key or default path.
	"""
	try:
		if not os.path.isfile(os.environ.get(environ_key, default_path)):
			raise ValueError('Define %s error!' % environ_key)
		with open(os.environ.get(environ_key, default_path), 'r') as file:
			return json.loads(file.read())
	except Exception as exc:
		logging.error(getattr(exc, 'message', repr(exc)))
		sys.exit(0)


# Define configuration and localization
CONFIG = define_from(CONFIG_PATH_KEY, CONFIG_PATH)
LOCALE = define_from(LOCALE_PATH_KEY, LOCALE_PATH)


def define_list(folder: str, extension: str) -> list:
	"""
	Return list of filenames from folder with defined extension.
	"""
	try:
		if not os.path.exists(folder):
			raise ValueError('Define %s error!' % folder)
		result = []
		for filename in os.listdir(folder):
			if filename.endswith(extension):
				result += [filename]
		return result
	except Exception as exc:
		logging.error(getattr(exc, 'message', repr(exc)))
		sys.exit(0)


# Application environment
BLUEPRINTS_NAME_WITH_URL_PREFIX = [
	('base', '/'),
	('avatar', '/avatar/'),
	('playlist', '/playlist/'),
	('gallery', '/gallery/')
]
BLUEPRINTS_ROOT_HANDLER = 'base.get_home'

# Initiate logging
if CONFIG.get('logging'):
	logging.basicConfig(
		format=CONFIG['logging'].get('format'),
		level=CONFIG['logging'].get('level')
	)
