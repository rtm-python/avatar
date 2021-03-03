# -*- coding: utf-8 -*-

"""
Blueprint module to handle landing routes.
"""

# Standard libraries import
import logging

# Application modules import
from blueprints.base import blueprint
from blueprints.__init__ import SignedInUser
from identica import IdenticaManager
from models.user_store import UserStore
from models.entity.user import User

# Additional libraries import
from flask import render_template
from flask import url_for
from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user
from flask import redirect
from flask import request
from flask import url_for
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField


class SignInForm(FlaskForm):
	"""
	This is a SignInForm class to retrieve form data.
	"""
	pin = StringField('signInPin')
	password = StringField('signInPassword')
	submit = SubmitField('signInSubmit')

	def __init__(self) -> "SignInForm":
		"""
		Initiate object with values from request.
		"""
		super(SignInForm, self).__init__()
		for field in self:
			if field.name != 'csrf_token':
				data = request.form.get(field.label.text)
				field.data = data if data is not None and len(data) > 0 else None


@blueprint.route('/sign/in/', methods=('GET','POST'))
def sign_in():
	"""
	Return sign in page.
	"""
	if current_user.is_authenticated:
		return redirect(url_for('base.get_home'))
	form = SignInForm()
	if form.validate_on_submit() and form.pin.data is not None:
		if form.password.data is None:
			password = IdenticaManager.get_password(form.pin.data)
			if password is None:
				return redirect(url_for('base.sign_in'))
			form.password.data = password
		else:
			verify_data = IdenticaManager.verify_pin(form.pin.data)
			if verify_data is None:
				return { 'redirect': url_for('base.sign_in') }
			elif verify_data.get('from'):
				user = UserStore.get_or_create_user(
					verify_data['from']['id'],
					verify_data['from']['first_name'],
					verify_data['from']['last_name'],
					verify_data['from']['username']
				)
				login_user(SignedInUser(user), remember=True)
				logging.debug('Sign in as user %s (%s)' % \
					(' '.join([user.first_name, user.last_name]), user.from_id))
				return { 'redirect': url_for('base.get_home') }
			return { 'wait': True }
	with open('source/static/face.txt', 'r') as file:
		ascii_img = file.read().split('\n')
	return render_template(
		'base/sign_in.html',
		form=form,
		ascii_img=ascii_img
	)


@blueprint.route('/sign/out/', methods=('GET',))
def sign_out():
	"""
	Return home page after sign out.
	"""
	if current_user.is_authenticated:
		logout_user()
	return redirect(url_for('base.get_home'))


@blueprint.route('/', methods=('GET',))
def get_home():
	"""
	Return home page.
	"""
	with open('source/static/face.txt', 'r') as file:
		ascii_img = file.read().split('\n')
	return render_template(
		'base/home.html',
		ascii_img=ascii_img
	)
