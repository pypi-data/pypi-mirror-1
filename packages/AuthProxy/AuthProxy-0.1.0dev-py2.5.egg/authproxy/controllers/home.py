import logging

from authproxy.lib.base import *

log = logging.getLogger(__name__)

class HomeController(BaseController):

    def index(self):
        # Return a rendered template
        #   return render('/some/template.mako')
        # or, Return a response
        return render('genshi','index')
