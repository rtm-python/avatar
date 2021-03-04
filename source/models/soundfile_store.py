# -*- coding: utf-8 -*-

'''
Store module for soundfile entity.
'''

# Stabdard libraries import
from datetime import datetime

# Application modules import
from models import database
from models import Store
from models.entity.soundfile import Soundfile

# Additional libraries import
from sqlalchemy import and_
from sqlalchemy import or_


class SoundfileStore(Store):
	"""
	This is a soundfile class.
	"""

	@staticmethod
	def create(name: str, description: str, filename: str,
						 order_utc: datetime, used: bool) -> Soundfile:
		"""
		Create and return soundfile.
		"""
		return super(SoundfileStore, SoundfileStore).create(
			Soundfile(
				name, description, filename, order_utc, used
			)
		)

	@staticmethod
	def read(uid: str) -> Soundfile:
		"""
		Return soundfile by uid (only not deleted).
		"""
		return super(SoundfileStore, SoundfileStore).read(
			Soundfile, uid
		)

	@staticmethod
	def update(uid: str, name: str, description: str, filename: str,
						 used: bool) -> Soundfile:
		"""
		Update and return soundfile.
		"""
		soundfile = SoundfileStore.read(uid)
		soundfile.name = name
		soundfile.description = description
		soundfile.filename = filename
		soundfile.used = used
		return super(SoundfileStore, SoundfileStore).update(
			soundfile
		)

	@staticmethod
	def delete(uid: str) -> Soundfile:
		"""
		Delete and return soundfile.
		"""
		return super(SoundfileStore, SoundfileStore).delete(
			SoundfileStore.read(uid)
		)

	@staticmethod
	def reorder(uid: str, order_utc: datetime) -> Soundfile:
		"""
		Update order_utc and return soundfile.
		"""
		soundfile = super(SoundfileStore, SoundfileStore).read(
			Soundfile, uid
		)
		soundfile.order_utc = order_utc
		return super(SoundfileStore, SoundfileStore).update(
			soundfile
		)

	@staticmethod
	def read_list(offset: int, limit: int,
							  name: str, description: str, filename: str,
								used: bool) -> list:
		"""
		Return list of soundfile by arguments.
		"""
		return _get_list_query(
			name, description, filename, used
		).limit(limit).offset(offset).all()

	@staticmethod
	def count_list(name: str, description: str, filename: str,
								 used: bool) -> list:
		"""
		Return list of soundfile by arguments.
		"""
		return Store.count(_get_list_query(
			name, description, filename, used
		))


def _get_list_query(name: str, description: str, filename: str,
										used: bool):
	"""
	Return query object for soundfile based on arguments.
	"""
	utcnow = datetime.utcnow()
	return database.session.query(
		Soundfile
	).filter(
		True if name is None else \
			Soundfile.name.ilike('%' + name + '%'),
		True if description is None else \
			Soundfile.description.ilike('%' + description + '%'),
		True if filename is None else \
			Soundfile.filename.ilike('%' + filename + '%'),
		True if used is None else \
			Soundfile.used == used,
		Soundfile.deleted_utc == None
	).order_by(
			Soundfile.order_utc.desc()
	)
