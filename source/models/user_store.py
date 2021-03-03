# -*- coding: utf-8 -*-

'''
Store module for User entity.
'''

# Application modules import
from models import database
from models import Store
from models.entity.user import User


class UserStore(Store):
	"""
	This is a user class.
	"""

	@staticmethod
	def create(from_id: str,
						 first_name: str, last_name: str, username: str) -> User:
		"""
		Create and return user.
		"""
		return super(UserStore, UserStore).create(
			User(from_id, first_name, last_name, username)
		)

	@staticmethod
	def read(uid: str) -> User:
		"""
		Return user by uid (only not deleted).
		"""
		return super(UserStore, UserStore).read(
			User, uid
		)

	@staticmethod
	def update(uid: str, from_id: str,
						 first_name: str, last_name: str, username: str) -> User:
		"""
		Update and return user.
		"""
		user = UserStore.read(uid)
		user.from_id = from_id
		user.first_name = first_name
		user.last_name = last_name
		user.username = username
		return super(UserStore, UserStore).update(
			user
		)

	@staticmethod
	def delete(uid: str) -> User:
		"""
		Delete and return user.
		"""
		return super(UserStore, UserStore).delete(
			UserStore.read(uid)
		)

	@staticmethod
	def read_list(offset: int, limit: int,
							  filter_name: str
								) -> list:
		"""
		Return list of users by arguments.
		"""
		return _get_list_query(
			filter_name
		).limit(limit).offset(offset).all()

	@staticmethod
	def count_list(filter_name: str) -> int:
		"""
		Return number of users in list.
		"""
		return Store.count(_get_list_query(
			filter_name
		))

	@staticmethod
	def set_name(uid: str,
							 first_name: str, last_name: str, username: str) -> User:
		"""
		Set user name and return user.
		"""
		user = UserStore.read(uid)
		user.first_name = first_name
		user.last_name = last_name
		user.username = username
		return super(UserStore, UserStore).update(
			user
		)

	@staticmethod
	def get(id: int) -> User:
		"""
		Return user by id (no matter deleted or etc.).
		"""
		return super(UserStore, UserStore).get(
			User, id
		)

	@staticmethod
	def get_or_create_user(from_id: str,
												 first_name: str, last_name: str,
												 username: str) -> User:
		"""
		Return user by from_id (only not deleted).
		"""
		user = database.session.query(
			User
		).filter(
			from_id == User.from_id,
			User.deleted_utc == None
		).first()
		if user is None:
			user = UserStore.create(from_id, first_name, last_name, username)
		else:
			UserStore.update(user.uid, from_id, first_name, last_name, username)
		return user


def _get_list_query(filter_name: str):
	"""
	Return query object for user based on arguments.
	"""
	return database.session.query(
		User
	).filter(
		True if filter_name is None else \
			User.first_name.contains(filter_name),
		True if filter_name is None else \
			User.last_name.contains(filter_name),
		True if filter_name is None else \
			User.username.contains(filter_name),
		User.deleted_utc == None
	).order_by(
		User.modified_utc.desc()
	)
