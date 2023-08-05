from pylons import Response, c, g, h, cache, request, session
from pylons.controllers import WSGIController
from pylons.decorators import jsonify, rest, validate
from pylons.templating import render, render_response
from pylons.helpers import abort, redirect_to
import quickwiki.models as model

from sqlalchemy import *

class BaseController(WSGIController):
    def __call__(self, environ, start_response):
        model.meta.connect(
            request.environ['paste.config']['app_conf']['dsn']
        )
        objectstore.clear()
        response = WSGIController.__call__(self, environ, start_response)
        objectstore.flush()
        return response



