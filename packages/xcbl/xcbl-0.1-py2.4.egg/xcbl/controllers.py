import logging

import cherrypy

import turbogears
from turbogears import controllers, expose, validate, redirect

from xcbl import json

log = logging.getLogger("xcbl.controllers")

class Root(controllers.RootController):
    @expose(template="xcbl.templates.welcome")
    def index(self):
        import time
        log.debug("Happy TurboGears Controller Responding For Duty")
        return dict(now=time.ctime())
