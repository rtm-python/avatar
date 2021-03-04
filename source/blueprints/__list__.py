# -*- coding: utf-8 -*-

"""
Blueprint module to define filter form.
"""

# Standard libraries import
import sys
import math
import json
import datetime
import importlib
import logging

# Application modules import
import blueprints

# Additional libraries import
from flask import request
from flask import url_for
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SelectField
from wtforms import BooleanField
from wtforms import SubmitField


class FilterForm(FlaskForm):
	"""
	This is FilterForm class to retrieve form data.
	"""
	__abstract__ = True
	prefix = None

	def __init__(self, prefix: str) -> 'FilterForm':
		"""
		Initiate object with values from request
		"""
		super(FilterForm, self).__init__()
		self.prefix = prefix
		for field in self:
			if field.name != 'csrf_token':
				data = request.form.get(self.prefix + field.label.text)
				field.data = data if data is not None and len(data) > 0 else None

	def define_fields(self) -> None:
		"""
		Set form fields to values from request.
		"""
		if blueprints.get_value(self.prefix + 'FilterReset', bool, False):
			for field in self:
				if field.name != 'csrf_token':
					if type(field) is StringField or type(field) is BooleanField:
						field.data = None
						blueprints.set_value(self.prefix + field.label.text, None)
					elif type(field) is SelectField:
						field.data = field.choices[0][0]
						blueprints.set_value(
							self.prefix + field.label.text, field.choices[0][0])
		else:
			for field in self:
				if field.name != 'csrf_token':
					data = field.data
					if type(field) is StringField:
						field.data = \
							blueprints.get_value(self.prefix + field.label.text, str, None)
					elif type(field) is SelectField:
						field.data = \
							blueprints.get_value(
								self.prefix + field.label.text, str,
								field.choices[0][0] \
									if field.choices[0][0] != '' else None
							)
					elif type(field) is BooleanField:
						field.data = \
							blueprints.get_value(self.prefix + field.label.text, bool, False)

	def store_fields(self) -> None:
		"""
		Set form fields to values from request.
		"""
		for field in self:
			if type(field) is StringField or type(field) is BooleanField:
				blueprints.set_value(self.prefix + field.label.text, field.data)
			elif type(field) is SelectField:
				blueprints.set_value(
					self.prefix + field.label.text,
					field.data \
						if field.data is not None and \
							field.data != field.choices[0] else None
				)

	def url_for_with_fields(self, endpoint: str) -> object:
		"""
		Return url_for with defined form fields.
		"""
		filter_kwargs = {}
		for field in self:
			if type(field) is StringField or type(field) is BooleanField:
				filter_kwargs[self.prefix + field.label.text] = field.data
			elif type(field) is SelectField:
				filter_kwargs[self.prefix + field.label.text] = field.data \
					if field.data is not None and \
						field.data != field.choices[0][0] else None
		return url_for(endpoint, **filter_kwargs)

	def is_submit(self, submit_name: str) -> bool:
		"""
		Return True if submit is presented otherwise False.
		"""
		return not request.form.get(self.prefix + submit_name) is None


class Pagination():
	"""
	This is a Pagination class to handle pages.
	"""
	endpoint = None
	entity_count = None
	page_index = None
	per_page= None
	page_count = None

	def __init__(self, prefix: str, endpoint: str, entity_count: int,
							 default_per_page: int = 12) -> "Pagination":
		"""
		Initiate pagination object with values.
		"""
		super().__init__()
		self.endpoint = endpoint
		self.entity_count = entity_count
		# Set prefix value names
		self.prefixed_page_index = '%sPageIndex' % prefix
		self.prefixed_per_page = '%sPerPage' % prefix
		# Get page_index and per_page from request
		self.page_index = blueprints.get_value(
			self.prefixed_page_index, int, 1)
		self.per_page = blueprints.get_value(
			self.prefixed_per_page, int, default_per_page)
		# Calculate page_count
		self.page_count = int(math.modf(entity_count / self.per_page)[1])
		if self.page_count < self.entity_count / self.per_page:
			self.page_count = self.page_count + 1
		# Check page_index and per_page validity
		if self.page_index < 1:
			self.page_index = 1
		elif self.page_index > self.page_count:
			self.page_index = self.page_count
		if self.per_page < 1:
			self.per_page = 1
		# Store arguments in session
		blueprints.set_value(self.prefixed_page_index, self.page_index)
		blueprints.set_value(self.prefixed_per_page, self.per_page)


	def url_for(self, page_index: int = None, per_page: int = None,
							on_verified_pages: bool = False) -> str:
		"""
		Return url_for defined page_index.
		"""
		verify_page_index = self.page_index \
			if page_index is None else page_index
		verify_per_page = self.per_page \
			if per_page is None else per_page
		if on_verified_pages and \
				(
					verify_page_index < 1 or \
					verify_page_index > self.page_count or \
					verify_per_page < 1
				):
			return
		return url_for(
			self.endpoint,
			**{
				self.prefixed_page_index: page_index,
				self.prefixed_per_page: per_page
			}
		)

	def url_for_prev(self) -> str:
		"""
		Return url_for for previous page (if possible).
		"""
		return self.url_for(
			page_index=self.page_index - 1, on_verified_pages=True)

	def url_for_next(self) -> str:
		"""
		Return url_for for next page (if possible).
		"""
		return self.url_for(
			page_index=self.page_index + 1, on_verified_pages=True)


class PaginatorForm(FilterForm):
	"""
	This is PaginatorForm class to retrieve form data.
	"""
	page_index = StringField('PageIndex')
	submit = SubmitField('PaginatorSubmit')

	def __init__(self, name: str) -> "PaginatorForm":
		"""
		Initiate object with values from request.
		"""
		super(PaginatorForm, self).__init__(name)
