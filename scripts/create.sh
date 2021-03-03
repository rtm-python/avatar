#!/usr/bin/env bash

PWD="$(pwd)"
BASENAME="${PWD##*/}"

# -------------------------

cat << EOM

Application source
-- source/
----- blueprints/
-------- base/
----------- __init__.py
----------- landing.py
-------- __init__.py
----- models/
-------- entity/
----------- __init__.py
-------- __init__.py
----- templates/
-------- base/
----------- base/
-------------- landing.html
-------------- error.html
-------- layout.html
-------- layout_inner.html
-------- layout_landing.html
----- static/
-------- image/
-------- css/
-------- js/
----- run.py
----- config.py
----- locale.json

EOM

[ ! -d source ] \
	&& mkdir source \
	&& echo '[+] Folder "source" created' \
	|| echo '[-] Folder "source" already exists'

# -------------------------

read -r -d '' CONTENT << EOM
# -*- coding: utf-8 -*-

"""
Main module to run application.
"""

# Standard libraries import
import logging
import sys

# Append source path on wsgi initialization
sys.path.append('source')

# Application moudles import
from blueprints import application
from models import database
from config import CONFIG

# Run application on executing module
if __name__ == '__main__':
	application.run(CONFIG['web']['host'], CONFIG['web']['port'])

EOM

[ ! -f source/run.py ] \
	&& echo -e "$CONTENT" > source/run.py \
	&& echo '[+] Module "run.py" created' \
	|| echo '[-] Module "run.py" already exists'

# -------------------------

read -r -d '' CONTENT << EOM
# -*- coding: utf-8 -*-

"""
Configuration module to define application variables and constants.
"""

# Standard libraries import
import os
import sys
import json
import logging
from enum import Enum

# Environment value keys
CONFIG_PATH_KEY = '${BASENAME^^}_CONFIG_PATH'
LOCALE_PATH_KEY = '${BASENAME^^}_LOCALE_PATH'

# Application constants
CONFIG_PATH = 'config/app.json'
LOCALE_PATH = 'source/locale.json'
STATIC_PATH = 'source/static'
TEMPLATE_PATH = 'source/templates'
DATABASE_PATH = 'database'


def define_from(environ_key: str, default_path: str) -> dict:
	"""
	Return dictionary from json-file
	defined by environment key or default path.
	"""
	try:
		if not os.path.isfile(os.environ.get(environ_key, default_path)):
			raise ValueError('Define %s error!' % environ_key)
		with open(os.environ.get(environ_key, default_path), 'r') as file:
			return json.loads(file.read())
	except Exception as exc:
		logging.error(getattr(exc, 'message', repr(exc)))
		sys.exit(0)


# Define configuration and localization
CONFIG = define_from(CONFIG_PATH_KEY, CONFIG_PATH)
LOCALE = define_from(LOCALE_PATH_KEY, LOCALE_PATH)


def define_list(folder: str, extension: str) -> list:
	"""
	Return list of filenames from folder with defined extension.
	"""
	try:
		if not os.path.exists(folder):
			raise ValueError('Define %s error!' % folder)
		result = []
		for filename in os.listdir(folder):
			if filename.endswith(extension):
				result += [filename]
		return result
	except Exception as exc:
		logging.error(getattr(exc, 'message', repr(exc)))
		sys.exit(0)


# Application environment
BLUEPRINTS_NAME_WITH_URL_PREFIX = [
	('base', '/')
]
BLUEPRINTS_ROOT_HANDLER = 'base.get_landing'

# Initiate logging
if CONFIG.get('logging'):
	logging.basicConfig(
		format=CONFIG['logging'].get('format'),
		level=CONFIG['logging'].get('level')
	)

EOM

[ ! -f source/config.py ] \
	&& echo -e "$CONTENT" > source/config.py \
	&& echo '[+] Module "config.py" created' \
	|| echo '[-] Module "config.py" already exists'

# -------------------------

read -r -d '' CONTENT << EOM
{
	"__": {
		"supported_languages": ["kz", "ru", "en"]
	},
	"language": {
		"endpoint": null,
		"en": "language",
		"ru": "язык"
	}
}
EOM

[ ! -f source/locale.json ] \
	&& echo -e "$CONTENT" > source/locale.json \
	&& echo '[+] Module "locale.json" created' \
	|| echo '[-] Module "locale.json" already exists'

# -------------------------

[ ! -d source/blueprints ] \
	&& mkdir source/blueprints \
	&& echo '[+] Folder "source/blueprints" created' \
	|| echo '[-] Folder "source/blueprints" already exists'

# -------------------------

read -r -d '' CONTENT << EOM
# -*- coding: utf-8 -*-

"""
Initial blueprints module to define blueprints.
"""

# Standard libraries import
import secrets
import importlib
import json

# Application modules import
from config import CONFIG
from config import LOCALE
from config import STATIC_PATH
from config import TEMPLATE_PATH
from config import BLUEPRINTS_NAME_WITH_URL_PREFIX
from config import BLUEPRINTS_ROOT_HANDLER

# Additional libraries import
from flask import Flask
from flask import session
from flask import request
from flask_paranoid import Paranoid
from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import AnonymousUserMixin

# Initiate Flask object
application = Flask(
	CONFIG['name'], static_url_path='',
	static_folder=STATIC_PATH, template_folder=TEMPLATE_PATH
)
application.config['SECRET_KEY'] = CONFIG['web']['secret_key']


class SignedInUser(UserMixin):
	"""
	This is a SignedInUser class to handle data of authenticated user.
	"""

	def __init__(self, user):
		super().__init__()
		self.user = user

	def get_id(self):
		"""
		Return uid for linked to SignedInUser object User entity.
		"""
		if self.user is not None:
			return self.user.uid

	def get_token(self):
		"""
		Return None for SignedInUser object (no anonymous token).
		"""
		return None


class AnonymousUser(AnonymousUserMixin):
	"""
	This is a AnonymousUser class to handle data of anonymous user.
	"""

	def get_id(self):
		"""
		Return None for AnonymousUser object (no user uid).
		"""
		return None

	def get_token(self):
		"""
		Return anonymous token for anonymous user.
		"""
		anonymous_token = session.get('anonymous_token')
		if anonymous_token is None:
			anonymous_token = secrets.token_hex(256)
			session['anonymous_token'] = anonymous_token
		return anonymous_token


# Initiate LoginManager object
login_manager = LoginManager(application)
login_manager.anonymous_user = AnonymousUser
login_manager.session_protection = 'strong'

# Import and register blueprint modules
# (prevent circular imports)
for module_name, url_prefix in BLUEPRINTS_NAME_WITH_URL_PREFIX:
	module = importlib.import_module('blueprints.%s' % module_name)
	application.register_blueprint(module.blueprint, url_prefix=url_prefix)

# Initiate Paranoid object
paranoid = Paranoid(application)
paranoid.redirect_view = BLUEPRINTS_ROOT_HANDLER

# Import UserStore from models
from models import UserStore


@login_manager.user_loader
def load_user(user_id):
	"""
	Return SignedInUser object linked to User entity by uid.
	"""
	return SignedInUser(UserStore.read(user_id))


@application.before_request
def make_session_permanent():
	"""
	Make all sessions permanent.
	"""
	session.permanent = True


@application.before_request
def set_session_language():
	"""
	Set session language from client request.
	"""
#	session['language'] = 'ru'
	session['language'] = request.accept_languages.best_match(
		LOCALE['__']['supported_languages']
	)


@application.context_processor
def get_dictionary():
	"""
	Return dictionary from text string.
	"""
	def _dict(text: str) -> dict:
		return __dict(text)
	return dict(__dict=__dict)


def __dict(text: str) -> dict:
	"""
	Return dictionary from text string.
	"""
	return json.loads(text)


@application.context_processor
def get_config():
	"""
	Return configuration data by key.
	"""
	def _config(key: str) -> object:
		return __config(key)
	return dict(__config=__config)


def __config(key: str) -> object:
	"""
	Return configuration data by key.
	"""
	return CONFIG.get(key)


@application.context_processor
def get_localized():
	"""
	Return localized text string.
	"""
	def _(key: str) -> str:
		return __(key)
	return dict(__=__)


def __(key: str) -> str:
	"""
	Return matching by key localized text string.
	"""
	value = LOCALE.get(key)
	if value:
		localized = value.get(session['language'])
		if localized:
			return localized
	return key


def get_value(name: str, default) -> object:
	"""
	Return cast to default type value from request or session.
	"""
	for args in [request.args, session.get('args') or {}]:
		value = args.get(name)
		if value is not None:
			try:
				default_type = type(default)
				if default_type is int:
					return int(value)
				elif default_type is str:
					return str(value)
				elif define_type is bool:
					return value == 'true' or value == 'True' or \
						value == 'on' or value is True
			except:
				logging.warning('Value casting error!')


def set_value(name: str, value: int) -> None:
	"""
	Set name, value pair to session args dictionary.
	"""
	args = session.get('args') or {}
	args[name] = value
	session['args'] = args

EOM

[ ! -f source/blueprints/__init__.py ] \
	&& echo -e "$CONTENT" > source/blueprints/__init__.py \
	&& echo '[+] Module "blueprints/__init__.py" created' \
	|| echo '[-] Module "blueprints/__init__.py" already exists'

# -------------------------

[ ! -d source/blueprints/base ] \
	&& mkdir source/blueprints/base \
	&& echo '[+] Folder "source/blueprints/base" created' \
	|| echo '[-] Folder "source/blueprints/base" already exists'

# -------------------------

read -r -d '' CONTENT << EOM
# -*- coding: utf-8 -*-

"""
Initial blueprint module to initiate base blueprint.
"""

# Standard libraries import
import os

# Application modules import
from blueprints import application
from config import STATIC_PATH
from config import TEMPLATE_PATH

# Additional libraries import
from flask import Blueprint
from flask import render_template

# Initiate Blueprint object
blueprint = Blueprint(
	'base', __name__,
	static_folder=STATIC_PATH, template_folder=TEMPLATE_PATH
)

# Routes handlers import (after blueprint initiatiing)
from blueprints.base import landing


@application.errorhandler(400) # HTTP_400_BAD_REQUEST
@application.errorhandler(401) # HTTP_401_UNAUTHORIZED
@application.errorhandler(403) # HTTP_403_FORBIDDEN
@application.errorhandler(404) # HTTP_404_NOT_FOUND
@application.errorhandler(405) # HTTP_405_METHOD_NOT_ALLOWED
@application.errorhandler(406) # HTTP_406_NOT_ACCEPTABLE
@application.errorhandler(408) # HTTP_408_REQUEST_TIMEOUT
@application.errorhandler(409) # HTTP_409_CONFLICT
@application.errorhandler(410) # HTTP_410_GONE
@application.errorhandler(411) # HTTP_411_LENGTH_REQUIRED
@application.errorhandler(412) # HTTP_412_PRECONDITION_FAILED
@application.errorhandler(413) # HTTP_413_REQUEST_ENTITY_TOO_LARGE
@application.errorhandler(414) # HTTP_414_REQUEST_URI_TOO_LONG
@application.errorhandler(415) # HTTP_415_UNSUPPORTED_MEDIA_TYPE
@application.errorhandler(416) # HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE
@application.errorhandler(417) # HTTP_417_EXPECTATION_FAILED
@application.errorhandler(428) # HTTP_428_PRECONDITION_REQUIRED
@application.errorhandler(429) # HTTP_429_TOO_MANY_REQUESTS
@application.errorhandler(431) # HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE
@application.errorhandler(500) # HTTP_500_INTERNAL_SERVER_ERROR
@application.errorhandler(501) # HTTP_501_NOT_IMPLEMENTED
@application.errorhandler(502) # HTTP_502_BAD_GATEWAY
@application.errorhandler(503) # HTTP_503_SERVICE_UNAVAILABLE
@application.errorhandler(504) # HTTP_504_GATEWAY_TIMEOUT
@application.errorhandler(505) # HTTP_505_HTTP_VERSION_NOT_SUPPORTED
def handle_error(error):
	"""
	Return error message.
	"""
	error_code=getattr(error, 'code', 0)
	return render_template(
		'base/error.html',
		error_code=error_code
	), error_code

EOM

[ ! -f source/blueprints/base/__init__.py ] \
	&& echo -e "$CONTENT" > source/blueprints/base/__init__.py \
	&& echo '[+] Module "blueprints/base/__init__.py" created' \
	|| echo '[-] Module "blueprints/base/__init__.py" already exists'

# -------------------------

read -r -d '' CONTENT << EOM
# -*- coding: utf-8 -*-

"""
Blueprint module to handle landing routes.
"""

# Application modules import
from blueprints.base import blueprint

# Additional libraries import
from flask import render_template


@blueprint.route('/', methods=('GET',))
@blueprint.route('/landing/', methods=('GET',))
def get_landing():
	"""
	Return landing page.
	"""
	return render_template(
		'base/landing.html'
	)

EOM

[ ! -f source/blueprints/base/landing.py ] \
	&& echo -e "$CONTENT" > source/blueprints/base/landing.py \
	&& echo '[+] Module "blueprints/base/landing.py" created' \
	|| echo '[-] Module "blueprints/base/landing.py" already exists'

# -------------------------

[ ! -d source/models ] \
	&& mkdir source/models \
	&& echo '[+] Folder "source/models" created' \
	|| echo '[-] Folder "source/models" already exists'

# -------------------------

read -r -d '' CONTENT << EOM
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
	application.config['SQLALCHEMY_DATABASE_URI'] = CONFIG['database']['URI'] + \
		os.path.join(database_folder, CONFIG['database']['filename'])
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
database = SQLAlchemy(application)
migrate = Migrate(application, database, directory=database_folder)

# Entity modules import (prevent circular import)
# from models.entity import <entity_module>
from models.entity import Entity


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


# from user_store import UserStore


class UserStore(Store):
	"""
	Temporary store class for user loader (should be deleted)
	"""
	
	@staticmethod
	def read(uid: str) -> None:
		"""
		Return None.
		"""
		return None

EOM

[ ! -f source/models/__init__.py ] \
	&& echo -e "$CONTENT" > source/models/__init__.py \
	&& echo '[+] Module "models/__init__.py" created' \
	|| echo '[-] Module "models/__init__.py" already exists'

# -------------------------

[ ! -d source/models/entity ] \
	&& mkdir source/models/entity \
	&& echo '[+] Folder "source/models/entity" created' \
	|| echo '[-] Folder "source/models/entity" already exists'

# -------------------------

read -r -d '' CONTENT << 'EOM'
# -*- coding: utf-8 -*-

"""
Initial module to initiate entities.
"""

# Standard libraries import
import uuid
import datetime

# Application modules import
from models import database

# Additional libraries import
from sqlalchemy import Column


class Entity(database.Model):
	"""
	Abstract class for database entities
	with entity's uid and deleted_utc field.
	Also object string representation implemented.
	"""
	__abstract__ = True
	id = Column(database.Integer, primary_key=True)
	uid = Column(database.String)
	created_utc = Column(database.DateTime)
	modified_utc = Column(database.DateTime)
	deleted_utc = Column(database.DateTime)

	def __init__(self):
		"""
		Initiate object, generate uid for entity
		and set created utc value to current datetime.
		"""
		self.uid = str(uuid.uuid4())
		self.created_utc = datetime.datetime.utcnow()
		self.modified_utc = self.created_utc

	def set_modified(self):
		"""
		Set modified utc value to current datetime.
		"""
		self.modified_utc = datetime.datetime.utcnow()

	def set_deleted(self):
		"""
		Set deleted utc value to current datetime.
		"""
		self.deleted_utc = datetime.datetime.utcnow()
		self.modified_utc = self.deleted_utc

	def __str__(self):
		"""
		Generates object's string representation for possible debug purposes.
		"""
		return '\\r\\n'.join(
			['%s: %s' % (attr, getattr(self, attr))
				for attr in dir(self) if not attr.startswith('_') and \
					not callable(getattr(self, attr))]
		)

EOM

[ ! -f source/models/entity/__init__.py ] \
	&& echo -e "$CONTENT" > source/models/entity/__init__.py \
	&& echo '[+] Module "models/entity/__init__.py" created' \
	|| echo '[-] Module "models/entity/__init__.py" already exists'

# -------------------------

[ ! -d source/templates ] \
	&& mkdir source/templates \
	&& echo '[+] Folder "source/templates" created' \
	|| echo '[-] Folder "source/templates" already exists'

# -------------------------

read -r -d '' CONTENT << 'EOM'
{%- set basename = __config('name') -%}
<!DOCTYPE html>
<html>
	<head lang="en">
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=yes">
		<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous"/>
		<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/tempusdominus-bootstrap-4/5.0.0-alpha14/css/tempusdominus-bootstrap-4.min.css" />
		<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Comfortaa|Marmelad|Open+Sans+Condensed:300&display=swap"/>
		<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/open-iconic/1.1.1/font/css/open-iconic-bootstrap.min.css" integrity="sha256-BJ/G+e+y7bQdrYkS2RBTyNfBHpA9IuGaPmf9htub5MQ=" crossorigin="anonymous"/>
		<link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@500&display=swap" rel="stylesheet"> 
		<link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='favicon_w.ico') }}?v=1.0"/>
		{%- block style -%}{%- endblock -%}
		<title>{{ __(basename) }}{%- if title -%}{{ ': ' + title }}{%- endif -%}</title>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js" integrity="sha512-bLT0Qm9VnAYZDflyKcBaQ2gg0hSYNQrJ8RilYldYQ1FxQYoCLtUjuuRuZo+fjqhx/qtq/1itJ0C2ejDxltZVFg==" crossorigin="anonymous"></script>		<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/2.4.2/umd/popper.min.js" integrity="sha256-XahKYIZhnEztrOcCTmaEErjYDLoLqBoDJbVMYybyjH8=" crossorigin="anonymous"></script>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/2.5.4/umd/popper.min.js" integrity="sha512-7yA/d79yIhHPvcrSiB8S/7TyX0OxlccU8F/kuB8mHYjLlF1MInPbEohpoqfz0AILoq5hoD7lELZAYYHbyeEjag==" crossorigin="anonymous"></script>
		<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.27.0/moment-with-locales.min.js" integrity="sha256-wdiCkHJlqyoIJxG49WbDO0D3/EnppQp6GVOGQA6PBkA=" crossorigin="anonymous"></script>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/moment-timezone/0.5.31/moment-timezone-with-data.min.js" integrity="sha256-E10X63Z5YvTXDfZjb0Kqd7FOo6a/gE7hFGcYm63PLmM=" crossorigin="anonymous"></script>
		<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/tempusdominus-bootstrap-4/5.0.0-alpha14/js/tempusdominus-bootstrap-4.min.js"></script>
		{%- if not ga_disable and False -%}
			<!-- Global site tag (gtag.js) - Google Analytics -->
			<script async src="https://www.googletagmanager.com/gtag/js?id=<ga_id>"></script>
			<script>
				window.dataLayer = window.dataLayer || [];
				function gtag(){dataLayer.push(arguments);}
				gtag('js', new Date());
				gtag('config', '<ga_id>');
			</script>
		{%- endif -%}
    {%- block script -%}{%- endblock -%}
	</head>
	{%- block body -%}{%- endblock -%}
</html>
EOM

[ ! -f source/templates/layout.html ] \
	&& echo -e "$CONTENT" > source/templates/layout.html \
	&& echo '[+] Template "templates/layout.html" created' \
	|| echo '[-] Template "templates/layout.html" already exists'

# -------------------------

read -r -d '' CONTENT << 'EOM'
{%- extends "layout.html" -%}
{%- block style -%}
		<meta name="theme-color" content="#563d7c">
    <style>
      .bd-placeholder-img {
        font-size: 1.125rem;
        text-anchor: middle;
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        user-select: none;
      }
      @media (min-width: 768px) {
        .bd-placeholder-img-lg {
          font-size: 3.5rem;
        }
      }
    </style>
    <link href="{{ url_for('static', filename='cover.css') }}" rel="stylesheet">
{%- endblock -%}
{%- block body -%}
  <body class="text-center">
    <div class="cover-container d-flex w-100 h-100 p-3 mx-auto flex-column">
		  <header class="masthead mb-auto">
		    <div class="inner">
		      <a class="navbar-brand p-0 m-0" href="{{ url_for('base.get_landing') }}">
		      	<img class="d-inline align-middle mr-2" src="{{ url_for('static', filename='est_w.png') }}" width="25" height="25">
		      	<strong>{{ __(basename) }}</strong>
		      </a>
		      <nav class="nav nav-masthead justify-content-center">
		        <a class="nav-link" href="#">{{ __('Item 1') }}</a>
		        <a class="nav-link" href="#">{{ __('Item 2') }}</a>
		        <a class="nav-link" href="#">{{ __('Item 3') }}</a>
		        {%- if current_user and current_user.is_authenticated -%}
			        <a class="nav-link" href="#"><span class="oi oi-person"></span></a>
			      {%- else -%}
			        <a class="nav-link" href="#"><span class="oi oi-account-login"></span></a>
			      {%- endif -%}
		      </nav>
		    </div>
		  </header>
		  <main role="main" class="inner cover">
		  	{%- block body_content -%}{%- endblock -%}
		  </main>
		  <footer class="mastfoot mt-auto">
		    <div class="inner text-center">- P1A7CK/2021 -</div>
		  </footer>
		</div>
	  {%- block body_script -%}{%- endblock -%}
	</body>
{%- endblock -%}
EOM

[ ! -f source/templates/layout_landing.html ] \
	&& echo -e "$CONTENT" > source/templates/layout_landing.html \
	&& echo '[+] Template "templates/layout_landing.html" created' \
	|| echo '[-] Template "templates/layout_landing.html" already exists'

# -------------------------

read -r -d '' CONTENT << 'EOM'
{%- extends "layout.html" -%}
{%- block body -%}
	<body class="d-flex flex-column h-100">
		<header>
			<nav class="navbar navbar-expand-md navbar-dark fixed-top bg-dark">
				<a class="navbar-brand" href="{{ url_for('base.get_landing') }}">
					<img class="d-inline align-middle mr-2" src="{{ url_for('static', filename='est_w.png') }}" width="25" height="25">
					<strong class="d-inline">{{ __(basename) }}</strong>
				</a>
				<button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarCollapse" aria-controls="navbarCollapse" aria-expanded="false" aria-label="Toggle navigation">
				  <span class="navbar-toggler-icon"></span>
				</button>
				<div class="collapse navbar-collapse justify-content-md-end" id="navbarCollapse">
				  <ul class="navbar-nav">
				    <li class="nav-item {% if nav_active == 'item_2' %}active{% endif %}"><a class="nav-link" href="#">{{ __('Item 1') }}</a></li>
				    <li class="nav-item {% if nav_active == 'item_2' %}active{% endif %}"><a class="nav-link" href="#"">{{ __('Item 2') }}</a></li>
				    <li class="nav-item {% if nav_active == 'item_3' %}active{% endif %}"><a class="nav-link" href="#">{{ __('Item 3') }}</a> </li>
				    <li class="nav-item {% if nav_active == 'item_4' %}active{% endif %}">
				    	{%- if current_user and current_user.is_authenticated -%}
					      <a class="nav-link" href="#"><span class="oi oi-person"></span></a>
					    {%- else -%}
					      <a class="nav-link" href="#"><span class="oi oi-account-login"></span></a>
					    {%- endif -%}
				    </li>
				  </ul>
				</div>
			</nav>
		</header>
		<div class="container-fluid mt-5">
			<h4 class="mt-4 text-center"><strong>{{ title }}</strong></h4>
			<hr class="mt-3 mb-3" style="border-color: whitesmoke;"/>
			{%- block body_content -%}{%- endblock -%}
			<footer class="mastfoot mt-auto">
				<div class="inner text-center">- P1A7CK/2021 -</div>
			</footer>
		</div>
		{%- block body_script -%}{%- endblock -%}
	</body>
{%- endblock -%}
EOM

[ ! -f source/templates/layout_inner.html ] \
	&& echo -e "$CONTENT" > source/templates/layout_inner.html \
	&& echo '[+] Template "templates/layout_inner.html" created' \
	|| echo '[-] Template "templates/layout_inner.html" already exists'

# -------------------------

[ ! -d source/templates/base ] \
	&& mkdir source/templates/base \
	&& echo '[+] Folder "source/templates/base" created' \
	|| echo '[-] Folder "source/templates/base" already exists'

# -------------------------

read -r -d '' CONTENT << 'EOM'
{%- extends "layout_landing.html" -%}
{%- block body_content -%}
	{%- if info_templates -%}
		{% set language = __('language') %}
		<div id="carouselExampleCaptions" class="carousel slide" data-ride="carousel">
			<ol class="carousel-indicators mb-0">
				{%- for _ in info_templates -%}
				  <li data-target="#carouselExampleCaptions" data-slide-to="{{ loop.index0 }}" class="{% if loop.index0 == 0 %}{{ 'active' }}{%- endif -%}"></li>
				{%- endfor -%}
			</ol>
			<div class="carousel-inner">
				{%- for info_template in info_templates -%}
				  <div class="carousel-item{%- if loop.index0 == 0 -%}{{ ' active' }}{%- endif -%}" data-interval="10000">
						{%- include info_template -%}
				  </div>
				{%- endfor -%}
			</div>
			<a class="carousel-control-prev" href="#carouselExampleCaptions" role="button" data-slide="prev" style="width: 5%;">
			  <span class="carousel-control-prev-icon" aria-hidden="true"></span>
			  <span class="sr-only"></span>
			</a>
			<a class="carousel-control-next" href="#carouselExampleCaptions" role="button" data-slide="next" style="width: 5%;">
			  <span class="carousel-control-next-icon" aria-hidden="true"></span>
			  <span class="sr-only"></span>
			</a>
		</div>
	{%- endif -%}
{%- endblock -%}
EOM

[ ! -f source/templates/base/landing.html ] \
	&& echo -e "$CONTENT" > source/templates/base/landing.html \
	&& echo '[+] Template "templates/base/landing.html" created' \
	|| echo '[-] Template "templates/base/landing.html" already exists'

# -------------------------

read -r -d '' CONTENT << 'EOM'
{%- extends "layout_landing.html" -%}
{%- block body_content -%}
	<p class="text-center" style="font-family: 'Roboto Mono', monospace; font-size: 5vw;">{{ __('Error') }}</p>
	<h1 class="text-center" style="font-family: 'Roboto Mono', monospace; font-size: 20vw;">{{ error_code }}</h1>
{%- endblock -%}
EOM

[ ! -f source/templates/base/error.html ] \
	&& echo -e "$CONTENT" > source/templates/base/error.html \
	&& echo '[+] Template "templates/base/error.html" created' \
	|| echo '[-] Template "templates/base/error.html" already exists'

# -------------------------

# Static folder

[ ! -d source/static ] \
	&& mkdir source/static \
	&& echo '[+] Folder "source/static" created' \
	|| echo '[-] Folder "source/static" already exists'

[ ! -d source/static/image ] \
	&& mkdir source/static/image \
	&& echo '[+] Folder "source/static/image" created' \
	|| echo '[-] Folder "source/static/image" already exists'

[ ! -d source/static/css ] \
	&& mkdir source/static/css \
	&& echo '[+] Folder "source/static/css" created' \
	|| echo '[-] Folder "source/static/css" already exists'

[ ! -d source/static/js ] \
	&& mkdir source/static/js \
	&& echo '[+] Folder "source/static/js" created' \
	|| echo '[-] Folder "source/static/js" already exists'

echo 'Application source initiating complete.'
