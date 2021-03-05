# -*- coding: utf-8 -*-

'''
Store module for soundfile entity.
'''

# Stabdard libraries import
from datetime import datetime

# Application modules import
from models import database
from models import Store
from models import save_file
from models import delete_file
from models.entity.soundfile import Soundfile

# Additional libraries import
from sqlalchemy import and_
from sqlalchemy import or_


class SoundfileStore(Store):
	"""
	This is a soundfile class.
	"""

	@staticmethod
	def create(name: str, description: str,
						 file: object) -> Soundfile:
		"""
		Create and return soundfile.
		"""
		return super(SoundfileStore, SoundfileStore).create(
			Soundfile(
				name, description, save_file(file), datetime.utcnow(), False
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
	def update(uid: str, name: str, description: str,
						 file: object) -> Soundfile:
		"""
		Update and return soundfile.
		"""
		soundfile = SoundfileStore.read(uid)
		soundfile.name = name
		soundfile.description = description
		if file is not None:
			soundfile.filename = save_file(file, soundfile.filename)
		return super(SoundfileStore, SoundfileStore).update(
			soundfile
		)

	@staticmethod
	def delete(uid: str) -> Soundfile:
		"""
		Delete and return soundfile.
		"""
		soundfile = SoundfileStore.read(uid)
		delete_file(soundfile.filename)
		return super(SoundfileStore, SoundfileStore).delete(
			soundfile
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
							  name: str, description: str,
								used: bool) -> list:
		"""
		Return list of soundfile by arguments.
		"""
		return _get_list_query(
			name, description, used
		).limit(limit).offset(offset).all()

	@staticmethod
	def count_list(name: str, description: str,
								 used: bool) -> list:
		"""
		Return list of soundfile by arguments.
		"""
		return Store.count(_get_list_query(
			name, description, used
		))


def _get_list_query(name: str, description: str,
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
		True if used is None else \
			Soundfile.used == used,
		Soundfile.deleted_utc == None
	).order_by(
			Soundfile.order_utc.desc()
	)
