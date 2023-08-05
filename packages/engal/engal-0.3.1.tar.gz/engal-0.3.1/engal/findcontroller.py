import logging

import cherrypy

import turbogears
from turbogears import validate, redirect, expose
from turbogears import widgets, validators
from turbogears import error_handler, flash

from engal import json, model

log = logging.getLogger("engal.controllers")

from engal.ibox.widgets import Ibox
ibox = Ibox()

from resourcecontroller import Resource, expose_resource

class FindController(Resource):
    item_getter = model.TagAspect.byShort_name

#    @expose(template="engal.templates.tags")
#    def index(self):
#        return dict(aspects = model.TagAspect.select(), tag_form = tag_form, tagaspect_form = tagaspect_form, ibox = ibox)
    @expose(template="engal.templates.findwelcome")
    def index(self):
        return dict(aspects=model.TagAspect.select())

#    @expose()
#    @validate(form=tagaspect_form)
#    #@error_handler(index)
#    def addTagAspect(self, name, short_name, description, uri):
#        model.TagAspect.add(name=name, short_name=short_name, description=description, uri=uri)
#        flash("Tag aspect created")
#        raise redirect('/tags')
#
    @expose_resource
    @expose(template="engal.templates.findaspect")
    def show(self, tagaspect, tag = None):
        if tag:
            return self._showtag(tagaspect, tag)
        return dict(aspects=model.TagAspect.select(), aspect = tagaspect)

    @expose(template="engal.templates.findtag")
    def _showtag(self, tagaspect, tag):
        tag = model.Tag.byShort_name(tag)
        photos = tag.photos
        return dict(aspects=model.TagAspect.select(), aspect = tagaspect, tag = tag, photos = photos)

    @expose(template="engal.templates.findwelcome")
    def date(self):
        return dict(aspects=model.TagAspect.select())
#
#    @expose_resource
#    @expose()
#    def addTag(self, tagaspect, name, short_name, description, uri, tag_aspect):
#        root = model.Tag.getRoot(tagaspect)
#        t = model.Tag(name=name, short_name=short_name, description=description, uri=uri, aspect = tagaspect)
#        root.addChildNode(t)
#        flash("Tag created")
#        raise redirect('/tags/%s' % (tagaspect.short_name,))
