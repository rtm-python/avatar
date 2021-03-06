# -*- coding: utf-8 -*-

'''
Entity module for avatar entity.
'''

# Standard libraries import
from datetime import datetime

# Additional libraries import
from sqlalchemy import Column
from sqlalchemy import ForeignKey

# Project modules imports
from models import database
from models.entity import Entity


class Avatar(Entity):
	'''
	This is a class for avatar entity.
	'''
	__tablename__ = 'avatar'
	user_id = Column(
		database.Integer, ForeignKey('user.id'),
		index=True, nullable=False
	)
	soundfile_uid = Column(database.String, index=True, nullable=False)
	used = Column(database.Boolean, index=True, nullable=False)

	def __init__(self, user_id: int, soundfile_uid: str,
							 used: bool) -> "Soundfile":
		'''
		Initiate object and stores avatar's data.
		'''
		super().__init__()
		self.user_id = user_id
		self.soundfile = soundfile
		self.used = used
