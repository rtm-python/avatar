# -*- coding: utf-8 -*-

"""
Initial module to initiate database models and migrations.
"""

# Standard libraries import
import os

# Additional libraries import
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Application modules import
from config import CONFIG
from config import DATABASE_PATH
from blueprints import application

# Additional libraries import
from sqlalchemy import func

# Initiate database
database_folder = os.path.join(os.path.abspath(os.curdir), 'database')
if CONFIG['database']['filename'] is None:
	application.config['SQLALCHEMY_DATABASE_URI'] = CONFIG['database']['URI']
else:
	application.config['SQLALCHEMY_DATABASE_URI'] = CONFIG['database']['URI'] + 		os.path.join(database_folder, CONFIG['database']['filename'])
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
database = SQLAlchemy(application)
migrate = Migrate(application, database, directory=database_folder)

# Entity modules import (prevent circular import)
# from models.entity import <entity_module>
from models.entity import Entity
from models.entity import user


class Store():
	"""
	Abstract class for store objects.
	"""
	__abstract__ = True

	@staticmethod
	def create(entity: Entity) -> Entity:
		"""
		Create and return entity.
		"""
		database.session.add(entity)
		database.session.commit()
		return entity

	@staticmethod
	def read(entity_class, uid: str) -> Entity:
		"""
		Return entity by uid (only not deleted).
		"""
		return entity_class.query.filter_by(
			uid=uid, deleted_utc=None).first()

	@staticmethod
	def update(entity: Entity) -> Entity:
		"""
		Update and return entity.
		"""
		entity.set_modified()
		database.session.commit()
		return entity

	@staticmethod
	def delete(entity: Entity) -> Entity:
		"""
		Delete and return entity.
		"""
		entity.set_deleted()
		database.session.commit()
		return entity

	@staticmethod
	def get(entity_class, id: int) -> Entity:
		"""
		Return entity by id (no matter deleted or etc.).
		"""
		return entity_class.query.get(id)

	@staticmethod
	def count(query) -> int:
		"""
		Return number of elements (rows) in resulted query.
		"""
		return database.session.execute(
			query.statement.with_only_columns([func.count()]).order_by(None)
		).scalar() or 0


from models.user_store import UserStore
