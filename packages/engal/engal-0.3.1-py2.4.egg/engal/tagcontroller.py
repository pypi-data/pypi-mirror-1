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
from gallerycontroller import TagField

class TagFields(widgets.WidgetsList):
    tag_aspect = widgets.HiddenField()
    name = widgets.TextField(validator=validators.NotEmpty, label="Tag display name")
    short_name = widgets.TextField(validator=validators.NotEmpty, label="Tag short name")
    description = widgets.TextArea(validator=validators.NotEmpty, label="Tag description")
    uri = widgets.TextField(validator=validators.NotEmpty, label="Tag uri")
    parent_tag = widgets.HiddenField()

tag_form = widgets.TableForm(fields=TagFields(), submit_text="Add Tag")

class TagAspectFields(widgets.WidgetsList):
    name = widgets.TextField(validator=validators.NotEmpty, label="Tag display name")
    short_name = widgets.TextField(validator=validators.NotEmpty, label="Tag short name")
    description = widgets.TextArea(validator=validators.NotEmpty, label="Tag description")
    uri = widgets.TextField(validator=validators.NotEmpty, label="Tag uri")

tagaspect_form = widgets.TableForm(fields=TagAspectFields(), submit_text="Add Tag Aspect")

def _taglist():
    return [(tag.id, tag.name) for tag in model.Tag.select()]

class TagReparentFields(widgets.WidgetsList):
    tag = widgets.HiddenField(validator = validators.NotEmpty)
    parent_tag = widgets.SingleSelectField(validator=validators.NotEmpty)

tagparent_form = widgets.TableForm(fields=TagReparentFields(), submit_text = "Set parent tag")

class Tags(Resource):
    item_getter = model.TagAspect.byShort_name

    @expose(template="engal.templates.tagwelcome")
    def index(self):
        return dict(aspects = model.TagAspect.select(), tag_form = tag_form, tagaspect_form = tagaspect_form, ibox = ibox)

    @expose()
    @validate(form=tagaspect_form)
    #@error_handler(index)
    def addTagAspect(self, name, short_name, description, uri):
        model.TagAspect.add(name=name, short_name=short_name, description=description, uri=uri)
        flash("Tag aspect created")
        raise redirect('/tags')

    @expose_resource
    @expose(template="engal.templates.tagaspect")
    def show(self, tagaspect, tag = None):
        if tag:
            return self.showtag(tagaspect, tag)
        return dict(aspect = tagaspect, tag_form = tag_form, ibox=ibox)

    @expose(template="engal.templates.tag")
    def showtag(self, tagaspect, tag):
        tag = model.Tag.byShort_name(tag)
        q = model.Tag.q
        tags = model.Tag.select(model.NOT(model.AND(q.rgt <= tag.rgt, q.lft >= tag.lft)))
        parent_options = [(t.id, t.name) for t in tags if t.depth]
        parent_options.insert(0, (0, ""))
        return dict(aspect = tagaspect, tag = tag, tag_form = tag_form, ibox=ibox, tagparent_form = tagparent_form, parent_options = parent_options)

    @expose()
    @validate(form=tagparent_form)
    #@error_handler(index)
    def reparentTag(self, tag, parent_tag):
        tag = model.Tag.get(tag)
        parent_tag = model.Tag.get(parent_tag)
        parent_tag.addChildNode(tag)
        raise redirect('/tags/%s/%s' % (tag.aspect.short_name, tag.short_name))

    @expose_resource
    @expose()
    def addTag(self, tagaspect, name, short_name, description, uri, tag_aspect, parent_tag):
        if not parent_tag:
            parent_tag = model.Tag.getRoot(tagaspect)
        else:
            parent_tag = model.Tag.get(parent_tag)
        t = model.Tag(name=name, short_name=short_name, description=description, uri=uri, aspect = tagaspect)
        parent_tag.addChildNode(t)
        flash("Tag created")
        raise redirect('/tags/%s' % (tagaspect.short_name,))
