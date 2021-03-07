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
	def create(user_id: int, sid_data: str) -> Avatar:
		"""
		Create and return avatar.
		"""
		return super(AvatarStore, AvatarStore).create(
			Avatar(
				user_id, sid_data
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
	def update(uid: str, user_id: int, sid_data: str,
						 soundfile_uid: str) -> Avatar:
		"""
		Update and return avatar.
		"""
		avatar = AvatarStore.read(uid)
		avatar.user_id = user_id
		avatar.sid_data = sid_data
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
	def update_sid(uid: str, sid_data: str) -> Avatar:
		"""
		Update avatar sid_data and return avatar.
		"""
		avatar = super(AvatarStore, AvatarStore).read(
			Avatar, uid
		)
		avatar.sid_data = sid_data
		return super(AvatarStore, AvatarStore).update(
			avatar
		)

	@staticmethod
	def read_list(offset: int, limit: int,
							  user_id: int, sid_data: str,
							  soundfile_uid: str) -> list:
		"""
		Return list of avatar by arguments.
		"""
		return _get_list_query(
			user_id, sid_data, soundfile_uid
		).limit(limit).offset(offset).all()

	@staticmethod
	def count_list(user_id: int, sid_data: str,
								 soundfile_uid: str) -> list:
		"""
		Return list of avatar by arguments.
		"""
		return Store.count(_get_list_query(
			user_id, sid_data, soundfile_uid
		))


def _get_list_query(user_id: int, sid_data: str,
										soundfile_uid: str):
	"""
	Return query object for avatar based on arguments.
	"""
	return database.session.query(
		Avatar
	).filter(
		True if user_id is None else \
			Avatar.user_id == user_id,
		True if sid_data is None else \
			Avatar.sid_data.ilike('%' + sid_data + '%'),
		True if soundfile_uid is None else \
			Avatar.soundfile_uid == soundfile_uid,
		Avatar.deleted_utc == None
	).order_by(
			Avatar.modified_utc.desc()
	)
