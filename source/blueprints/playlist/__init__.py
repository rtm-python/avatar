# -*- coding: utf-8 -*-

"""
Initial blueprint module to initiate playlist blueprint.
"""

# Standard libraries import
import os

# Application modules import
from blueprints import application
from config import STATIC_PATH
from config import TEMPLATE_PATH

# Additional libraries import
from flask import Blueprint
from flask import render_template

# Initiate Blueprint object
blueprint = Blueprint(
	'playlist', __name__,
	static_folder=STATIC_PATH, template_folder=TEMPLATE_PATH
)

# Routes handlers import (after blueprint initiatiing)
from blueprints.playlist import playlist
