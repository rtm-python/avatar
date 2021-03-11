# -*- coding: utf-8 -*-

"""
Initial blueprint module to handle permission.
"""

# Standard libraries import
import os
import sys
import logging
from functools import wraps

# Application modules import
from models.permission_store import PermissionStore
from models.entity.permission import Permission
from models.user_store import UserStore
from models.entity.user import User

# Additional libraries import
from flask_login import current_user
from flask import redirect
from flask import url_for


def get_permissions(user_id: int) -> list:
	"""
	Get permissions for user.
	"""
	return [
		permission.value \
			for permission in PermissionStore.read_list(0, None, user_id, None)
	]


def add_permissions(user_id: int, permissions: list) -> None:
	"""
	Add permissions for user.
	"""
	current_permissions = get_permissions(user_id)
	for value in permissions:
		if value not in current_permissions:
			PermissionStore.create(user_id, value)
			current_permissions += [value]


def del_permissions(user_id: int, permissions: list) -> None:
	"""
	Del permissions for user.
	"""
	current_permissions = get_permissions(user_id)
	for value in permissions:
		if value in current_permissions:
			permission_list = PermissionStore.read_list(0, None, user_id, value)
			PermissionStore.delete(permission_list[0].uid)
			current_permissions.remove(value)


def permission_required(function):
	"""
	User permission to access verification decorator.
	"""
	@wraps(function)
	def wrapper(*args, **kwargs):
		"""
		Wrapper function to verify user permission.
		"""
		if not current_user.is_authenticated or \
				current_user.user is None:
			logging.debug('Redirect unauthorized (anonymous) user')
			return redirect(url_for('base.get_home'))
		permission_value = '%s.%s' % (
			function.__module__,
			function.__name__
		)
		permissions = PermissionStore.read_list(
			0, None, current_user.user.id, permission_value)
		if len(permissions) == 0:
			return redirect(url_for('base.get_home'))
		return function(*args, **kwargs)

	return wrapper


def get_choice(choices: list) -> int:
	"""
	Request user input and return integer value.
	"""
	while True:
		try:
			choice = int(input('\n'.join(choices) + '\n\nInput your choice: '))
			if choice < 0 or choice >= len(choices):
				raise ValueError()
			return choice
		except:
			print('Invalid choice, should be integer value in choices range\n')


def configure_permissions():
	"""
	Configure permissions.
	"""
	user = None
	level = 0
	while True:
		print()
		choice = None
		choices = []
		# Display
		if level == 0:
			user = None
			users = UserStore.read_list(0, None, None)
			choices = ['0: Exit'] + [
				'%d: %s (last login: %s) %s' % (
					index,
					' '.join([user.first_name, user.last_name]),
					user.modified_utc,
					user.uid
				) for index, user in enumerate(users, start=1)
			]
			choice = get_choice(choices)
		elif level == 1:
			choices = [
				'0: Back to users',
				'1: Add permission',
				'2: Delete permission',
				'3: Delete all permissions'
			]
			choice = get_choice(choices)
		elif level == 2:
			choices = ['0: Back to actions'] + [
				'1: blueprints.gallery.soundfile_catalog.get_soundfile_catalog',
				'2: blueprints.gallery.soundfile_catalog.upload_soundfile',
				'3: blueprints.gallery.soundfile_catalog.update_soundfile',
				'4: blueprints.gallery.soundfile_catalog.refresh_soundfile_catalog',
				'5: blueprints.gallery.soundfile_catalog.delete_soundfile',
				'6: blueprints.gallery.soundfile_catalog.get_audio',
				'7: blueprints.gallery.soundfile_catalog.get_image',
				'8: blueprints.playlist.playlist.get_playlist',
				'9: blueprints.avatar.player.get_player'
			]
			choice = get_choice(choices)
		elif level == 3:
			choices = ['0: Back to actions'] + [
				'%d: %s' % (
					index,
					permission
				)for permission in enumerate(permissionget_permissions(user.id))
			]
			choice = get_choice(choices)
		# Choice
		if level == 0 and choice == 0:
			break
		elif level == 0 and choice > 0:
			user = UserStore.read(choices[choice].split()[-1])
			print('\n'.join(['Current permissions:'] + get_permissions(user.id)))
			level = 1
		elif level == 1 and choice == 0:
			user = None
			level = 0
		elif level == 1 and choice == 1:
			level = 2
		elif level == 1 and choice == 2:
			level = 3
		elif level == 1 and choice == 3:
			permissions = get_permissions(user.id)
			del_permissions(user.id, permissions)
			print('Deleted permissions: %s' % permissions)
			level = 1
		elif level == 2 and choice == 0:
			level = 1
		elif level == 2 and choice > 0:
			add_permissions(user.id, [choices[choice].split(' ')[1]])
			print('Added permission: %s' % choices[choice])
			level = 2
		elif level == 3 and choice == 0:
			level = 1
		elif level == 3 and choice > 0:
			del_permissions(user.id, [choices[choice].split(' ')[1]])
			print('Deleted permission: %s' % choices[choice])
			level = 3
