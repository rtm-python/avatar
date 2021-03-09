# -*- coding: utf-8 -*-

"""
Blueprint module to handle soundfile catalog routes.
"""

# Stadnard libraries import
from datetime import datetime
from datetime import timedelta
import logging
import os

# Application modules import
from blueprints.__permission__ import permission_required
from blueprints.gallery import blueprint
import blueprints
from blueprints.__list__ import Pagination
from blueprints.__list__ import FilterForm
from blueprints.__list__ import PaginatorForm
from models.soundfile_store import SoundfileStore
from models.entity.soundfile import Soundfile
from models import send_file
from config import CONFIG
from config import GIFS_PATH
from config import PLUGINS_PATH
from config import define_list
from plugins.bubble import BubbleVideo

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
	used = SelectField('FilterUsed')
	submit = SubmitField('FilterSubmit')

	def __init__(self) -> "CatalogFilterForm":
		"""
		Initiate object with values from request.
		"""
		super(CatalogFilterForm, self).__init__('soundfileCatalog')
		self.used.choices = \
			[('used', 'Used')] + [('yes', 'Yes'), ('no', 'No')]


class RendererForm(FlaskForm):
	"""
	This is RendererForm class to retrieve form data.
	"""
	preset = SelectField('rendererPreset')
	duration = StringField('rendererDuration')
	submit = SubmitField('rendererSubmit')

	def __init__(self) -> "RendererForm":
		"""
		Initiate object with values from request.
		"""
		super(RendererForm, self).__init__()
		self.preset.choices = [('preset', 'Preset')] + \
			[
				(
					filename[: len(filename) - 4], filename[: len(filename) - 4]
				) for filename in define_list(PLUGINS_PATH, '.gif')
			]
		for field in self:
			if field.name != 'csrf_token':
				data = request.form.get(field.label.text)
				field.data = data if data is not None and len(data) > 0 else None


class SoundfileForm(FlaskForm):
	"""
	This is SoundfileForm class to retrieve form data.
	"""
	name = StringField('soundfileName')
	description = StringField('soundfileDescription')
	filename = StringField('soundfileFilename')
	submit = SubmitField('soundfileSubmit')

	def __init__(self, soundfile: Soundfile = None) -> "SoundfileForm":
		"""
		Initiate object with values from request.
		"""
		super(SoundfileForm, self).__init__()
		if soundfile:
			self.name.data = soundfile.name
			self.description.data = soundfile.description
			self.filename.data = soundfile.filename
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
		return is_valid

	def is_submit(self, submit_name: str) -> bool:
		"""
		Return True is submit is presented otherwise False.
		"""
		return not request.form.get(submit_name) is None

@blueprint.route('/', methods=('GET', 'POST'))
@blueprint.route('/soundfile/', methods=('GET', 'POST'))
@blueprint.route('/soundfile/catalog/', methods=('GET', 'POST'))
#@permission_required()
def get_soundfile_catalog():
	"""
	Return soundfile catalog page.
	"""
	if not current_user.is_authenticated:
		return redirect(url_for('base.get_home'))
	# Handle switching used attribute
	if request.json is not None and request.json.get('uid'):
		SoundfileStore.switch_used(
			request.json.get('uid'),
			request.json.get('checked')
		)
		return { 'ok': True }
	# Handle filter form
	filter = CatalogFilterForm()
	if filter.is_submit(filter.submit.label.text) and \
			filter.validate_on_submit():
		filter.store_fields()
		return redirect(filter.url_for_with_fields(
			'gallery.get_soundfile_catalog'))
	filter.define_fields()
	# Handle paginator form
	paginator = PaginatorForm('soundfileCatalog')
	if paginator.is_submit(paginator.submit.label.text) and \
			paginator.validate_on_submit():
		paginator.store_fields()
		return redirect(paginator.url_for_with_fields(
			'gallery.get_soundfile_catalog'))
	paginator.define_fields()
	# Prepare list data
	pagination = Pagination(
		'soundfileCatalog', 'gallery.get_soundfile_catalog',
		SoundfileStore.count_list(
			filter.name.data,
			filter.description.data,
			None \
				if filter.used.data == 'used' else filter.used.data == 'yes'
		)
	)
	soundfile_list = SoundfileStore.read_list(
		(pagination.page_index - 1) * pagination.per_page,
		pagination.per_page,
		filter.name.data,
		filter.description.data,
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


@blueprint.route('/soundfile/catalog/upload/', methods=('GET', 'POST'))
def upload_soundfile():
	"""
	Return soundfile upload page.
	"""
	if not current_user.is_authenticated:
		return redirect(url_for('base.get_home'))
	form = SoundfileForm()
	if form.validate_on_submit():
		if form.filename.data is None:
			form.filename.errors = ['Value required.']
		else:
			file = request.files.get('%sFile' % form.filename.label.text)
			if file is None or file.filename == '' or \
					file.content_type not in CONFIG['database']['allowed_types']:
				form.filename.errors = ['Invalid value.']
			else:
				soundfile = SoundfileStore.create(
					form.name.data, form.description.data, file, file.content_type
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
	if not current_user.is_authenticated:
		return redirect(url_for('base.get_home'))
	soundfile = SoundfileStore.read(uid)
	# Handle renderer form
	is_renderer_post = False
	renderer = RendererForm()
	if renderer.validate_on_submit() and \
			request.form.get(renderer.submit.label.text) is not None:
		if renderer.preset.data != renderer.preset.choices[0][0] and \
				renderer.duration.data is not None:
			try:
				duration = float(renderer.duration.data)
			except Exception as exc:
				duration = 0
			if duration > 0:
				preset_path = os.path.join(
					PLUGINS_PATH, '%s.gif' % renderer.preset.data)
				gif_path = os.path.join(GIFS_PATH, uid)
				frame_start = 0
				frame_count = int(1000 / 100 * duration) + 30
				print(frame_count)
				BubbleVideo.copy_gif(
					preset_path, gif_path, frame_start, frame_count, 85
				)
				return redirect(url_for('gallery.get_soundfile_catalog'))
		is_renderer_post = True
	# Handle soundfile form
	form = SoundfileForm(
		soundfile if request.method == 'GET' or is_renderer_post else None
	)
	if form.validate_on_submit() and \
			request.form.get(form.submit.label.text) is not None:
		if form.filename.data is None:
			form.filename.errors = ['Value required.']
		else:
			file = request.files.get('%sFile' % form.filename.label.text)
			if (file is None or file.filename == '' or \
					file.content_type not in CONFIG['database']['allowed_types']
					) and not form.filename.data.startswith('#'):
				form.filename.errors = ['Invalid value.']
			SoundfileStore.update(
				uid, form.name.data, form.description.data, file, file.content_type
			)
			return redirect(url_for('gallery.get_soundfile_catalog'))
	return render_template(
		'gallery/soundfile.html',
		form=form,
		renderer=renderer,
		audio_filename=soundfile.filename,
		audio_filetype=soundfile.filetype
	)


@blueprint.route('/soundfile/catalog/refresh/', methods=('GET',))
def refresh_soundfile_catalog():
	"""
	Refresh soundfile catalog (uncheck used) and return redirect.
	"""
	if not current_user.is_authenticated:
		return redirect(url_for('base.get_home'))
	SoundfileStore.refresh()
	return redirect(url_for('gallery.get_soundfile_catalog'))


@blueprint.route('/soundfile/catalog/delete/<uid>/', methods=('GET',))
def delete_soundfile(uid: str):
	"""
	Delete soundfile and return redirect page.
	"""
	if not current_user.is_authenticated:
		return redirect(url_for('base.get_home'))
	SoundfileStore.delete(
		uid
	)
	return redirect(url_for('gallery.get_soundfile_catalog'))


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
