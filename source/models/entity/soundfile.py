# -*- coding: utf-8 -*-

'''
Entity module for soundfile entity.
'''

# Standard libraries import
from datetime import datetime

# Additional libraries import
from sqlalchemy import Column

# Project modules imports
from models import database
from models.entity import Entity


class Soundfile(Entity):
	'''
	This is a class for soundfile entity.
	'''
	__tablename__ = 'soundfile'
	name = Column(database.String, index=True, nullable=False)
	description = Column(database.String, index=True, nullable=True)
	filename = Column(database.String, index=True, nullable=False)
	filetype = Column(database.String, index=True, nullable=False)
	order_utc = Column(database.DateTime, index=True, nullable=False)
	used = Column(database.Boolean, index=True, nullable=False)

	def __init__(self, name: str, description: str,
							 filename: str, filetype: str,
							 order_utc: datetime, used: bool) -> "Soundfile":
		'''
		Initiate object and stores soundfile's data.
		'''
		super().__init__()
		self.name = name
		self.description = description
		self.filename = filename
		self.filetype = filetype
		self.order_utc = order_utc
		self.used = used
