# -*- coding: utf-8 -*-

"""
Blueprint module to handle player routes.
"""

# Standard libraries import
import logging

# Application modules import
from blueprints.avatar import blueprint
#from models.user_store import UserStore
#from models.entity.user import User

# Additional libraries import
from flask import render_template
from flask import url_for
from flask_login import current_user
from flask import redirect
from flask import request
from flask import url_for
from flask import render_template


@blueprint.route('/player/', methods=('GET',))
def get_player():
	"""
	Return player page.
	"""
	if not current_user.is_authenticated:
		return redirect(url_for('base.get_home'))
	return render_template(
		'avatar/player.html'
	)
