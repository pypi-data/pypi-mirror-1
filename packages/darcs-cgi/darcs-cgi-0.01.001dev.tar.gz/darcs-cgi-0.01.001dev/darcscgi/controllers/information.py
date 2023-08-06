import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from darcscgi.lib.base import BaseController, render

from pylons import app_globals
from darcscgi.lib.helpers import filelisting

log = logging.getLogger(__name__)

class InformationController(BaseController):

    def redirect(self):
        redirect_to(controller='information', action='front')

    def front(self):
        return render('/information/front.mako')

    def repositories(self):
        return render('/information/repositories.mako')

    def quarantine(self):
        c.quarantinedFiles = filelisting(app_globals.globalSettings['quarantine-location'],0)
        return render('/information/quarantine.mako')
