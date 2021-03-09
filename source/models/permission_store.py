# -*- coding: utf-8 -*-

'''
Store module for permission entity.
'''

# Stabdard libraries import
from datetime import datetime

# Application modules import
from models import database
from models import Store
from models.entity.permission import Permission

# Additional libraries import
from sqlalchemy import and_
from sqlalchemy import or_


class PermissionStore(Store):
	"""
	This is a permission class.
	"""

	@staticmethod
	def create(user_id: int, value: str) -> Permission:
		"""
		Create and return permission.
		"""
		return super(PermissionStore, PermissionStore).create(
			Permission(
				user_id, value
			)
		)

	@staticmethod
	def read(uid: str) -> Permission:
		"""
		Return permission by uid (only not deleted).
		"""
		return super(PermissionStore, PermissionStore).read(
			Permission, uid
		)

	@staticmethod
	def update(uid: str, user_id: int, value: str) -> Permission:
		"""
		Update and return permission.
		"""
		permission = PermissionStore.read(uid)
		permission.user_id = user_id
		permission.value = value
		return super(PermissionStore, PermissionStore).update(
			permission
		)

	@staticmethod
	def delete(uid: str) -> Permission:
		"""
		Delete and return permission.
		"""
		return super(PermissionStore, PermissionStore).delete(
			PermissionStore.read(uid)
		)

	@staticmethod
	def read_list(offset: int, limit: int,
							  user_id: int, value: str) -> list:
		"""
		Return list of permission by arguments.
		"""
		return _get_list_query(
			user_id, value
		).limit(limit).offset(offset).all()

	@staticmethod
	def count_list(user_id: int, value: str) -> list:
		"""
		Return list of permission by arguments.
		"""
		return Store.count(_get_list_query(
			user_id, value
		))


def _get_list_query(user_id: int, value: str):
	"""
	Return query object for permission based on arguments.
	"""
	return database.session.query(
		Permission
	).filter(
		True if user_id is None else \
			Permission.user_id == user_id,
		True if value is None else \
			Permission.value == value,
		Permission.deleted_utc == None
	).order_by(
			Permission.modified_utc.desc()
	)
