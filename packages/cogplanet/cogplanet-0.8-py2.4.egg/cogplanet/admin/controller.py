import cherrypy

from turbogears import database
from turbogears import controllers, expose, url, error_handler
from turbogears import identity, redirect
from turbogears import validate
from turbogears import validators
from turbogears.widgets import *

from cogplanet.controllers import Restful
from cogplanet.model import *
from cogplanet.util import *

class PlanetFields(WidgetsList):
    id = HiddenField(name="id")
    name = TextField(name="name", attrs={'size':60})
    display_entries = TextField(name="display_entries",
                                label="Entries to display",
                                validator=validators.Number(),
                                attrs={'size': 60})
    update_interval = TextField(name="update_interval", 
                                label="Update Interval (Minutes)",
                                validator=validators.Number(),
                                attrs={'size': 60})

class PlanetForm(TableForm):
    fields = PlanetFields()
    submit_text = "Save Changes"

class FeedFields(WidgetsList):
    id = HiddenField(name="id")
    name = TextField(name="name", attrs={'size': 60})
    htmlurl = TextField(name="htmlurl", label="HTML URL", attrs={'size': 60})
    xmlurl = TextField(name="xmlurl", label="XML URL", attrs={'size': 60})
    updated_at = CalendarDateTimePicker(name="updated_at", label="Updated At")
    update_interval = TextField(name="update_interval", 
                                label="Update Interval (Minutes)",
                                validator=validators.Number(),
                                attrs={'size': 60})
    
class FeedForm(TableForm):
    fields = FeedFields()
    submit_text = "Save Changes"

class ImportFields(WidgetsList):
    opml_file = FileField(name="opml_file")

class ImportForm(TableForm):
    fields = ImportFields()
    submit_text = "Import Feeds"

class AdminController(controllers.Controller, Restful):
    feed_form = FeedForm()
    import_form = ImportForm()
    planet_form = PlanetForm()

    @expose()
    @identity.require(identity.in_group("cp_admin"))
    def delete(self, id):
        id = int(id)
        feed = Feed.selectone("id=%d" % id)
        feed.delete()
        raise cherrypy.HTTPRedirect("../")

    @expose(template="cogplanet.templates.admin.entry")
    @identity.require(identity.in_group("cp_admin"))
    def entry(self, id):
        entry = Entry.selectone(Entry.c.id==id)
        print entry.content
        planet = Planet.selectone()
        return({'entry':entry,
                'planet':planet})

    @expose(template="cogplanet.templates.admin.import_feeds")
    @validate(import_form)
    @identity.require(identity.in_group("cp_admin"))
    def import_feeds(self, opml_file=None):
        if opml_file != None:
            import_opml(opml_file.file)
        planet = Planet.selectone()
        # TODO should return the number of feeds imported
        return({'import_form': self.import_form,
                'planet':planet})

    @expose(template="cogplanet.templates.admin.planet")
    @identity.require(identity.in_group("cp_admin"))
    def planet_view(self):
        planet = Planet.selectone()
        return({'planet': planet,
                'planet_form': self.planet_form})

    @expose()
    @validate(planet_form)
    @error_handler(planet_view)
    @identity.require(identity.in_group("cp_admin"))
    def planet_update(self, **kw):
        planet = Planet.selectone()
        planet.name = kw['name']
        planet.display_entries = kw['display_entries']
        planet.update_interval = kw['update_interval']
        raise cherrypy.HTTPRedirect('./planet_view')

    @expose()
    @identity.require(identity.in_group("cp_admin"))
    def refresh(self, id):
        # TODO refresh should send the user back where they came from
        id = int(id)
        feed = Feed.selectone("id=%d" % id)
        feed.refresh_entries()
        raise cherrypy.HTTPRedirect(".")

    @expose()
    @validate(feed_form)
    @identity.require(identity.in_group("cp_admin"))
    def update(self, rest_id, **kw):
        print kw
        feed = None
        if rest_id == "new":
            feed = Feed()
        else:
            feed = Feed.selectone("id=%s" % rest_id)

        feed.name = kw["name"]
        feed.htmlurl = kw["htmlurl"]
        feed.xmlurl = kw["xmlurl"]
        feed.update_interval = kw["update_interval"]
        feed.save()

        database.session.context.current.flush()

        print "Feed id"
        print feed.id

        raise cherrypy.HTTPRedirect(url("/admin/%d/view" % feed.id))

    @expose(template="cogplanet.templates.admin.feed")
    @identity.require(identity.in_group("cp_admin"))
    def view(self, id):
        feed = {}
        if(id != 'new'):
            feed = Feed.selectone("id=%d" % int(id))
        planet = Planet.selectone()
        return({'feed': feed,
                'feed_form': self.feed_form,
                'planet': planet})

    @expose(template="cogplanet.templates.admin.index")
    @identity.require(identity.in_group("cp_admin"))
    def index(self):
        feeds = Feed.select(order_by="name")
        planet = Planet.selectone()
        return({"feeds": feeds,
                'planet': planet})
