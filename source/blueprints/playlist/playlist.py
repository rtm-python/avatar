# -*- coding: utf-8 -*-

"""
Blueprint module to handle playlist routes.
"""

# Stadnard libraries import
from datetime import datetime
from datetime import timedelta
import logging

# Application modules import
from blueprints.playlist import blueprint
import blueprints
from models.soundfile_store import SoundfileStore
from models.entity.soundfile import Soundfile
from models import send_file
from config import CONFIG

# Additional libraries import
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask_login import current_user


@blueprint.route('/', methods=('GET', 'POST'))
@blueprint.route('/playlist/', methods=('GET', 'POST'))
def get_playlist():
	"""
	Return playlist page.
	"""
	if not current_user.is_authenticated:
		return redirect(url_for('base.get_home'))
	# Handle reorderedList
	if request.json is not None and request.json.get('reorderedList'):
		order_utc = datetime.utcnow()
		for uid in request.json.get('reorderedList'):
			SoundfileStore.reorder(uid, order_utc)
			order_utc = order_utc - timedelta(microseconds=1)
		return redirect(url_for('playlist.get_playlist'))
	# Prepare list data
	soundfile_list = SoundfileStore.read_list(
		0, None, None, None, True
	)
	if blueprints.get_value('mobile', bool, False):
		blueprints.set_value('mobile', True)
	return render_template(
		'playlist/playlist.html',
		soundfile_list=soundfile_list,
		mobile=blueprints.get_value('mobile', bool, False)
	)


@blueprint.route('/soundfile/catalog/audio/<filename>/', methods=('GET',))
def get_audio(filename: str):
	"""
	Return audio file.
	"""
	if not current_user.is_authenticated:
		abort(403)
	return send_file(filename)
