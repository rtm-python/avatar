# -*- coding: utf-8 -*-

"""
Blueprint module to handle playlist routes.
"""

# Stadnard libraries import
from datetime import datetime
from datetime import timedelta
import logging
import json

# Application modules import
import blueprints
from blueprints.playlist import blueprint
from models.avatar_store import AvatarStore
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
	# Handle uidList (load data to avatar)
	if request.json is not None and request.json.get('uidList'):
		avatar_list = AvatarStore.read_list(
			None, 1, current_user.user.id, None, None
		)
		if len(avatar_list) > 0:
			avatar = avatar_list[0]
			sid_data = json.loads(avatar.sid_data)
			cleared_sid_list = []
			for uid in request.json['uidList']:
				soundfile = SoundfileStore.read(uid)
				for sid in sid_data['sid_list']:
					if sid not in cleared_sid_list:
						cleared_sid_list += [sid]
						blueprints.socketio.emit(
							'clear_data',
							{},
							room=sid,
							callback=blueprints.socketio_status
						)
					blueprints.socketio.emit(
						'load_data',
						{
							'uid': uid,
							'image': {
								'src': url_for(
									'playlist.get_image',
									filename='video2.gif'
								)
							},
							'audio': {
								'src': url_for(
									'gallery.get_audio', filename=soundfile.filename
								),
								'type': soundfile.filetype
							},
							'user': ' '.join([
								current_user.user.first_name,
								current_user.user.last_name
							]) if blueprints.socketio_authenticated() else ''
						},
						room=sid,
						callback=blueprints.socketio_status
					)
		return redirect(url_for('playlist.get_playlist'))
	# Handle uidPlay (play data to avatar)
	if request.json is not None and request.json.get('uidPlay'):
		avatar_list = AvatarStore.read_list(
			None, 1, current_user.user.id, None, None
		)
		if len(avatar_list) > 0:
			avatar = avatar_list[0]
			sid_data = json.loads(avatar.sid_data)
			uid = request.json.get('uidPlay')
			soundfile = SoundfileStore.read(uid)
			for sid in sid_data['sid_list']:
				blueprints.socketio.emit(
					'play_data',
					{
						'uid': uid,
						'image': {
							'src': url_for(
								'playlist.get_image',
								filename='video2.gif'
							)
						},
						'audio': {
							'src': url_for(
								'gallery.get_audio', filename=soundfile.filename
							),
							'type': soundfile.filetype
						},
						'user': ' '.join([
							current_user.user.first_name,
							current_user.user.last_name
						]) if blueprints.socketio_authenticated() else ''
					},
					room=sid,
					callback=blueprints.socketio_status
				)
		return {'ok': True}
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


@blueprint.route('/soundfile/catalog/image/<filename>/', methods=('GET',))
def get_image(filename: str):
	"""
	Return image file.
	"""
	if not current_user.is_authenticated:
		abort(403)
	return blueprints.send_image(filename)
