# -*- coding: utf-8 -*-

"""
Blueprint module to handle soundfile catalog routes.
"""

# Stadnard libraries import
from datetime import datetime
from datetime import timedelta
import logging

# Application modules import
from blueprints.gallery import blueprint
import blueprints
from blueprints.__list__ import Pagination
from blueprints.__list__ import FilterForm
from blueprints.__list__ import PaginatorForm
from models.soundfile_store import SoundfileStore
from models.entity.soundfile import Soundfile
from config import CONFIG

# Additional libraries import
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask_wtf import FlaskForm
from wtforms import validators
from wtforms import StringField
from wtforms import SelectField
from wtforms import SubmitField
from flask_login import current_user


class CatalogFilterForm(FilterForm):
	"""
	This is CatalogFilterForm class to retrieve form data.
	"""
	name = StringField('FilterName')
	description = StringField('FilterDescription')
	filename = StringField('FilterFilename')
	used = SelectField('FilterUsed')
	submit = SubmitField('FilterSubmit')

	def __init__(self) -> "CatalogFilterForm":
		"""
		Initiate object with values from request.
		"""
		super(CatalogFilterForm, self).__init__('soundfileCatalog')
		self.used.choices = \
			[('used', 'Used')] + [('yes', 'Yes'), ('no', 'No')]


class SoundfileForm(FlaskForm):
	"""
	This is SoundfileForm class to retrieve form data.
	"""
	name = StringField('soundfileName')
	description = StringField('soundfileDescription')
	filename = StringField('soundfileFilename')
	used = SelectField('soundfileUsed')
	submit = SubmitField('soundfileSubmit')

	def __init__(self, soundfile: Soundfile = None) -> "SoundfileForm":
		"""
		Initiate object with values from request.
		"""
		super(SoundfileForm, self).__init__()
		self.used.choices = \
			[('', 'Used')] + [('yes', 'Yes'), ('no', 'No')]
		if soundfile:
			self.name.data = soundfile.name
			self.description.data = soundfile.description
			self.filename.data = soundfile.filename
			self.used.data = 'yes' if soundfile.used else 'no'
		else:
			for field in self:
				if field.name != 'csrf_token':
					data = request.form.get(field.label.text)
					field.data = data if data is not None and len(data) > 0 else None

	def validate_on_submit(self) -> bool:
		"""
		Validate form fields values.
		"""
		is_valid = True
		if not super().validate_on_submit():
			if request.method == 'POST':
				is_valied = False
			else:
				return False
		if self.name.data is None or len(self.name.data) == 0:
			self.name.errors = ['Value required.']
			is_valid = False
		if self.used.data is None:
			self.used.errors = ['Invalid value.']
			is_valid = False
		return is_valid

	def is_submit(self, submit_name: str) -> bool:
		"""
		Return True is submit is presented otherwise False.
		"""
		return not request.form.get(submit_name) is None


@blueprint.route('/', methods=('GET', 'POST'))
@blueprint.route('/soundfile/', methods=('GET', 'POST'))
@blueprint.route('/soundfile/catalog/', methods=('GET', 'POST'))
def get_soundfile_catalog():
	"""
	Return soundfile catalog page.
	"""
	# Handle filter form
	filter = CatalogFilterForm()
	if filter.is_submit(filter.submit.label.text) and \
			filter.validate_on_submit():
		filter.store_fields()
		return redirect(filter.url_for_with_fields('soundfile.get_catalog'))
	filter.define_fields()
	# Handle paginator form
	paginator = PaginatorForm('soundfileCatalog')
	if paginator.is_submit(paginator.submit.label.text) and \
			paginator.validate_on_submit():
		paginator.store_fields()
		return redirect(paginator.url_for_with_fields('soundfile.get_catalog'))
	paginator.define_fields()
	# Prepare list data
	pagination = Pagination(
		'soundfileCatalog', 'soundfile.get_catalog',
		SoundfileStore.count_list(
			filter.name.data,
			filter.description.data,
			filter.filename.data,
			None \
				if filter.used.data == 'used' else filter.used.data == 'yes'
		)
	)
	soundfile_list = SoundfileStore.read_list(
		(pagination.page_index - 1) * pagination.per_page,
		pagination.per_page,
		filter.name.data,
		filter.description.data,
		filter.filename.data,
		None \
			if filter.used.data == 'used' else filter.used.data == 'yes'
	)
	return render_template(
		'gallery/soundfile_catalog.html',
		filter=filter,
		paginator=paginator,
		soundfile_list=soundfile_list,
		pagination=pagination
	)


@blueprint.route('/soundfile/catalog/create/', methods=('GET', 'POST'))
def create_soundfile():
	"""
	Return soundfile create page.
	"""
	form = SoundfileForm()
	if form.validate_on_submit():
		used = True if form.used.data == 'yes' else False
		soundfile = SoundfileStore.create(
			form.name.data, form.description.data, form.filename.data,
			datetime.utcnow(), used
		)
		return redirect(url_for('gallery.get_soundfile_catalog'))
	return render_template(
		'gallery/soundfile.html',
		form=form
	)


@blueprint.route('/soundfile/catalog/update/<uid>/', methods=('GET', 'POST'))
def update_soundfile(uid: str):
	"""
	Return soundfile update page.
	"""
	# Handle soundfile form
	form = SoundfileForm(
		SoundfileStore.read(uid) \
			if request.method == 'GET' else None
	)
	if form.validate_on_submit():
		used = True if form.used.data == 'yes' else False
		SoundfileStore.update(
			uid, form.name.data, form.description.data, form.filename.data,
			used
		)
		return redirect(url_for('galery.update_soundfile', uid=uid))
	return render_template(
		'gallery/soundfile.html',
		form=form
	)
