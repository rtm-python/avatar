# -*- coding: utf-8 -*-

"""
Initial blueprint module to initiate gallery blueprint.
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
	'gallery', __name__,
	static_folder=STATIC_PATH, template_folder=TEMPLATE_PATH
)

# Routes handlers import (after blueprint initiatiing)
from blueprints.gallery import soundfile_catalog
