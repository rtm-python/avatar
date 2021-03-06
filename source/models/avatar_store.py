# -*- coding: utf-8 -*-

'''
Store module for avatar entity.
'''

# Stabdard libraries import
from datetime import datetime

# Application modules import
from models import database
from models import Store
from models.entity.avatar import Avatar

# Additional libraries import
from sqlalchemy import and_
from sqlalchemy import or_


class AvatarStore(Store):
	"""
	This is a avatar class.
	"""

	@staticmethod
	def create(user_id: int, soundfile_uid: str) -> Avatar:
		"""
		Create and return avatar.
		"""
		return super(AvatarStore, AvatarStore).create(
			Avatar(
				user_id, soundfile_uid, False
			)
		)

	@staticmethod
	def read(uid: str) -> Avatar:
		"""
		Return avatar by uid (only not deleted).
		"""
		return super(AvatarStore, AvatarStore).read(
			Avatar, uid
		)

	@staticmethod
	def update(uid: str, user_id: int, soundfile_uid: str) -> Avatar:
		"""
		Update and return avatar.
		"""
		avatar = AvatarStore.read(uid)
		avatar.user_id = user_id
		avatar.soundfile_uid = soundfile_uid
		return super(AvatarStore, AvatarStore).update(
			avatar
		)

	@staticmethod
	def delete(uid: str) -> Avatar:
		"""
		Delete and return avatar.
		"""
		return super(AvatarStore, AvatarStore).delete(
			AvatarStore.read(uid)
		)

	@staticmethod
	def set_used(uid: str) -> Avatar:
		"""
		Switch avatar used attribute and return avatar.
		"""
		avatar = super(AvatarStore, AvatarStore).read(
			Avatar, uid
		)
		avatar.used = True
		return super(AvatarStore, AvatarStore).update(
			avatar
		)

	@staticmethod
	def read_list(offset: int, limit: int,
							  user_id: int, soundfile_uid: str,
								used: bool) -> list:
		"""
		Return list of avatar by arguments.
		"""
		return _get_list_query(
			user_id, soundfile_uid, used
		).limit(limit).offset(offset).all()

	@staticmethod
	def count_list(user_id: int, soundfile_uid: str,
								 used: bool) -> list:
		"""
		Return list of avatar by arguments.
		"""
		return Store.count(_get_list_query(
			user_id, soundfile_uid, used
		))


def _get_list_query(user_id: int, soundfile_uid: str,
										used: bool):
	"""
	Return query object for avatar based on arguments.
	"""
	return database.session.query(
		Avatar
	).filter(
		True if user_id is None else \
			Avatar.user_id == user_id,
		True if soundfile_uid is None else \
			Avatar.soundfile_uid == soundfile_uid,
		True if used is None else \
			Avatar.used == used,
		Avatar.deleted_utc == None
	).order_by(
			Avatar.modified_utc.desc()
	)
