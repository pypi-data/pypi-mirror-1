from turbogears import controllers, expose
from turbogears import identity, redirect
from cogplanet.model import *
from cogplanet import json
import cherrypy
from cherrypy import request, response
from genshi.template import MarkupTemplate

# import logging
# log = logging.getLogger("cogplanet.controllers")

class Restful:
    @expose()
    def default(self, *vpath, **params):
        if len(vpath) == 1:
            identifier = vpath[0]
            action = self.view
        elif len(vpath) == 2:
            identifier, verb = vpath
            verb = verb.replace('.', '_')
            action = getattr(self, verb, None)
            if not action:
                raise cherrypy.NotFound
            if not action.exposed:
                raise cherrypy.NotFound
        else:
            raise cherrypy.NotFound
        return action(identifier, **params)


from cogplanet.admin.controller import AdminController

class PlanetController(controllers.Controller, Restful):
    admin = AdminController()

    @expose(template="genshi:cogplanet.templates.index")
    # @identity.require(identity.in_group("admin"))
    def index(self):
        planet = Planet.selectone()
        entries = Entry.select(Entry.c.parsed == True, 
                               order_by="updated_at DESC", 
                               limit=planet.display_entries)
        feeds = Feed.select(order_by="name ASC")
        return {"entries":entries,
                "feeds":feeds,
                "planet": planet}

    @expose(template="genshi:cogplanet.templates.feeds")
    def feeds(self):
        feeds = Feed.select(order_by="name")
        planet = Planet.selectone()
        return({"feeds": feeds,
                "planet": planet})

    @expose(template="genshi:cogplanet.templates.login")
    def login(self, forward_url=None, previous_url=None, *args, **kw):

        if not identity.current.anonymous \
            and identity.was_login_attempted() \
            and not identity.get_identity_errors():
            raise redirect(forward_url)

        forward_url=None
        previous_url= request.path

        if identity.was_login_attempted():
            msg=_("The credentials you supplied were not correct or "
                   "did not grant access to this resource.")
        elif identity.get_identity_errors():
            msg=_("You must provide your credentials before accessing "
                   "this resource.")
        else:
            msg=_("Please log in.")
            forward_url= request.headers.get("Referer", "/")
            
        response.status=403
        planet = Planet.selectone()
        return dict(message=msg, previous_url=previous_url, logging_in=True,
                    original_parameters=request.params,
                    forward_url=forward_url,
                    planet=planet)

    @expose()
    def logout(self):
        identity.current.logout()
        raise redirect("/")
