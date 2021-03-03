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
from blueprints.base import home


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
