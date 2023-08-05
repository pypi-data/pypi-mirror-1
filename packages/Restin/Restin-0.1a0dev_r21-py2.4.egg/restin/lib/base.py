from pylons import Response, c, g, cache, request, session
from pylons.controllers import WSGIController
from pylons.decorators import jsonify, validate
from pylons.templating import render, render_response
from pylons.helpers import abort, redirect_to, etag_cache
from pylons.i18n import N_, _, ungettext

import restin.models as restin_model
import restin.lib.helpers as h

import restler


RestController = restler.BaseController(restin_model)


class BaseController(WSGIController): pass


__all__ = [__n for __n in locals().keys() if not __n.startswith('_')]
__all__.append('_')
