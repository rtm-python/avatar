# -*- coding: utf-8 -*-

"""
Blueprint module to handle player routes.
"""

# Standard libraries import
import logging
import json

# Application modules import
from blueprints.__permission__ import permission_required
import blueprints
from blueprints import socketio
from blueprints.avatar import blueprint
from models.user_store import UserStore
from models.avatar_store import AvatarStore
from models.soundfile_store import SoundfileStore
from models.entity.avatar import Avatar
from models.entity.soundfile import Soundfile

# Additional libraries import
from flask import render_template
from flask import url_for
from flask_login import current_user
from flask import redirect
from flask import request
from flask import url_for
from flask import render_template
from flask_socketio import disconnect


@blueprint.route('/player/', methods=('GET', 'POST'))
@permission_required
def get_player():
	"""
	Return player page.
	"""
	if not current_user.is_authenticated:
		return redirect(url_for('base.get_home'))
	if request.json is not None and request.json.get('uidPlay'):
		avatar_list = AvatarStore.read_list(
			1, 0, current_user.user.id, None, None
		)
		if len(avatar_list) > 0:
			avatar = avatar_list[0]
			sid_data = json.loads(avatar.sid_data)
	return render_template(
		'avatar/player.html'
	)


@socketio.on('connect')
@permission_required
def handle_connect():
	"""
	Create or update avatar with sid_data for connected user.
	"""
	avatar_list = AvatarStore.read_list(
		1, 0, current_user.user.id, None, None
	)
	if len(avatar_list) == 0:
		avatar = AvatarStore.create(
			current_user.user.id,
			json.dumps({'sid_list': [request.sid]})
		)
	else:
		avatar = avatar_list[0]
		sid_data = json.loads(avatar.sid_data)
		if request.sid not in sid_data['sid_list']:
			sid_data['sid_list'] += [request.sid]
		AvatarStore.update_sid(
			avatar.uid, json.dumps(sid_data)
		)
	logging.debug(
		'Avatar connected: %s (%s)' % (
			' '.join([current_user.user.first_name, current_user.user.last_name]),
			request.sid
		)
	)


@socketio.on('disconnect')
@permission_required
def handle_disconnect():
	"""
	Remove sid from avatar for disconnected user.
	"""
	avatar_list = AvatarStore.read_list(
		1, None, current_user.user.id, None, None
	)
	if len(avatar_list) > 0:
		avatar = avatar_list[0]
		sid_data = json.loads(avatar.sid_data)
		if request.sid in sid_data['sid_list']:
			sid_data['sid_list'].remove(request.sid)
		AvatarStore.update_sid(
			avatar.uid, json.dumps(sid_data)
		)
	logging.debug(
		'Avatar disconnected: %s (%s)' % (
			' '.join([current_user.user.first_name, current_user.user.last_name]),
			request.sid
		)
	)


@socketio.on('avatar_connected')
@permission_required
def handle_avatar_connected(data):
	logging.debug(
		'%s [Avatar: %s] connected with loaded data: %s' % (
			' '.join([
				current_user.user.first_name,
				current_user.user.last_name
			]) if blueprints.socketio_authenticated() else 'Anonymous User',
			request.sid, data
		)
	)
	socketio.emit(
		'clear_data',
		{
			'avatar_list': data.get('avatar_list')
		},
		room=request.sid,
		callback=blueprints.socketio_status
	)
