import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from darcscgi.lib.base import BaseController, render

log = logging.getLogger(__name__)

class TemplateController(BaseController):

    def stylesheets(self, sheet):
        response.content_type = 'text/css'
        return render('/stylesheets/'+sheet)
