# -*- coding: utf-8 -*-

"""
Blueprint module to handle player routes.
"""

# Standard libraries import
import logging

# Application modules import
from blueprints import socketio
from blueprints.avatar import blueprint
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


@blueprint.route('/player/', methods=('GET', 'POST'))
def get_player():
	"""
	Return player page.
	"""
	if not current_user.is_authenticated:
		return redirect(url_for('base.get_home'))
	if request.method == 'POST':
		avatar_list = AvatarStore.read_list(
			0, 1, current_user.user.id, None, False
		)
		if avatar_list is None or len(avatar_list) == 0:
			return {}
		avatar = avatar_list[0]
		AvatarStore.set_used(avatar.uid)
		return { "soundfile_uid": avatar.soundfile_uid }
	return render_template(
		'avatar/player.html'
	)


@socketio.on('avatar_connected')
def handle_avatar_connected(json):
	print('Avatar Connected: %s' % json)
