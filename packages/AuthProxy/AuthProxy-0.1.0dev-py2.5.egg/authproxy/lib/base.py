"""The base Controller API

Provides the BaseController class for subclassing, and other objects
utilized by Controllers.
"""
from pylons import c, cache, config, g, request, response, session
from pylons.controllers import WSGIController
from pylons.controllers.util import abort, etag_cache, redirect_to
from pylons.decorators import jsonify, validate
from pylons.i18n import _, ungettext, N_
from pylons.templating import render

import authproxy.lib.helpers as h


class BaseController(WSGIController):

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        try:
            return WSGIController.__call__(self, environ, start_response)
        finally:
            pass

    def __before__(self, action, **params):
        """
           XXX palliatif bug authkit-0.4 :
           charger environ authkit.users
        """
        #self.users=request.environ["authkit.users"]



# Include the '_' function in the public names
__all__ = [__name for __name in locals().keys() if not __name.startswith('_') \
           or __name == '_']
