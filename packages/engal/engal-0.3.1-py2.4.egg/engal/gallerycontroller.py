import cherrypy

import turbogears
from turbogears import controllers, expose, validate, redirect
from turbogears import identity, widgets, validators, mochikit
from turbogears import error_handler, flash

from engal import json, model

import logging
log = logging.getLogger("engal.gallerycontroller")

from engal.ibox.widgets import Ibox
ibox = Ibox()

from resourcecontroller import Resource, expose_resource

from engal.util import getTagIconDirectory

class PhotoSetFields(widgets.WidgetsList):
    name = widgets.TextField(validator=validators.NotEmpty)
    title = widgets.TextField(validator=validators.NotEmpty)
    description = widgets.TextArea()
    return_path = widgets.HiddenField()

photoset_form = widgets.TableForm(fields=PhotoSetFields(),
                                 submit_text="Add set")

class PhotoFields(widgets.WidgetsList):
    file = widgets.FileField()
    name = widgets.TextField(validator=validators.NotEmpty)
    description = widgets.TextArea()
    return_path = widgets.HiddenField()
    photoset_id = widgets.HiddenField(validator=validators.Int)

photo_form = widgets.TableForm(fields=PhotoFields(),
                                 submit_text="Add Photo")

class EditPhotoFields(widgets.WidgetsList):
    name = widgets.TextField(validator=validators.NotEmpty)
    description = widgets.TextArea()
    return_path = widgets.HiddenField()
    photo_id = widgets.HiddenField(validator=validators.Int)

editphoto_form = widgets.TableForm(fields=EditPhotoFields(),
                                 submit_text="Edit Photo")

class DefinitionForm(widgets.Form):
    template = """
    <form xmlns:py="http://purl.org/kid/ns#"
        name="${name}"
        action="${action}"
        method="${method}"
        class="tableform"
        py:attrs="form_attrs"
    >
        <div py:for="field in hidden_fields"
            py:replace="field.display(value_for(field), **params_for(field))"
        />
        <dl>
            <div py:for="i, field in enumerate(fields)"
                class="${i%2 and 'odd' or 'even'}"
            >
                <dt>
                    <label class="fieldlabel" for="${field.field_id}" py:content="field.label" />
                </dt>
                <dd>
                    <span py:replace="field.display(value_for(field), **params_for(field))" />
                    <span py:if="error_for(field)" class="fielderror" py:content="error_for(field)" />
                    <span py:if="field.help_text" class="fieldhelp" py:content="field.help_text" />
                </dd>
            </div>
            <div>
                <dt>&#160;</dt>
                <dd py:content="submit.display(submit_text)" />
            </div>
        </dl>
    </form>
    """


class TagField(widgets.SingleSelectField):
    params = ["aspect", "photo", "tag"]
    aspect = None
    photo = None
    tag = None

    def _extend_options(self, d):
        if not self.aspect:
            d = [(tag.id, tag.name) for tag in model.Tag.select() if tag.depth and tag != self.tag]
        elif not self.photo:
            d = [(tag.id, tag.name) for tag in self.aspect.tags if tag.depth and tag != self.tag]
        else:
            d = [(tag.id, tag.name) for tag in self.aspect.tags if tag.depth and tag not in self.photo.tags and tag != self.tag]
        d.insert(0, (0, ""))
        return d

class TagWidgets(widgets.FieldSet):
    template="""
    <fieldset xmlns:py="http://purl.org/kid/ns#"
        class="${field_class}"
        id="${field_id}"
    >
        <legend py:if="legend" py:content="legend" />
        <div py:for="field in hidden_fields"
            py:replace="field.display(value_for(field), **params_for(field))"
        />
        <table>
        <tr py:for="field in fields">
            <td><label class="fieldlabel" for="${field.field_id}" py:content="field.label" /></td>
            <td>
            <span py:content="field.display(value_for(field), **params_for(field))" />
            <span py:if="error_for(field)" class="fielderror" py:content="error_for(field)" />
            <span py:if="field.help_text" class="fieldhelp" py:content="field.help_text" />
            </td>
        </tr>
        </table>
    </fieldset>
    """

    def iter_member_widgets(self):
        aspects = model.TagAspect.select()
        for aspect in aspects:
            yield TagField(label=aspect.name, aspect = aspect, name=aspect.short_name)

    def update_params(self, d):
        super(TagWidgets, self).update_params(d)
        d["fields"] = self.iter_member_widgets()
        log.info(str(d))

class TagFields(widgets.WidgetsList):
    tags = TagWidgets(label="Add new tags")
    photo_id = widgets.HiddenField()
    return_url = widgets.HiddenField()

tag_form = DefinitionForm(fields=TagFields(), submit_text="Change tags")

widgets.register_static_directory("engal.tagicons", getTagIconDirectory())

class TagCSS(widgets.CSSSource):
    src = """.engal_tag {
    padding-left: 25px;
    font-size: smaller;
    background-position: top left;
    background-repeat: no-repeat;
    background-color: transparent;
    background-image: url(%(root)s/tg_widgets/engal.tagicons/default.png);
    }

    .engal_tags {
        padding-bottom: 1em;
    }

    """

    src_aspect = """.engal_tag.engal_tagaspect_%(name)s {
        background-image: url(%(root)s/tg_widgets/engal.tagicons/%(id)s);
    }"""

    def __init__(self, *args, **kw):
        super(TagCSS, self).__init__(self.src, *args, **kw)

    def update_params(self, d):
        #self(TagCSS, self).update_params(d)
        d['src'] = self.buildSource()

    def buildSource(self):
        ret = []
        ret.append(self.src % dict(root=turbogears.url("")))
        for aspect in model.TagAspect.select():
            if aspect.hasIcon():
                ret.append(self.src_aspect % dict(name=aspect.short_name, root=turbogears.url(""), id=aspect.id))
        return "\n".join(ret)

class TagInfo(widgets.Widget):
    css = [TagCSS()]

    def __init__(self, tag_info, *args, **kw):
        self.tag_info = tag_info
        super(TagInfo, self).__init__(*args, **kw)

    def items(self):
        return self.tag_info

class Gallery(Resource):
    item_getter = model.User.by_user_name
    friendly_item_name = "user"

    @expose(template="engal.templates.gallery_frontpage")
    def index(self):
        users = model.User.select()
        if not users.count():
            raise redirect("/firstuser")
        return dict(users = users)

    @expose(template="engal.templates.userpage")
    def show(self, user, *args, **kw):
        tg_errors = kw.get('tg_errors', None)
        photosets = model.PhotoSet.select(user == user)
        if tg_errors:
            flash("There was a problem with the form!")
        return dict(photosets = photosets, ibox = ibox, photoset_form = photoset_form, mochikit = mochikit, user = user)

    @expose_resource
    @expose(template="engal.templates.photosets")
    def sets(self, user, name = None, tg_errors = None):
        if not name:
            return self.show(user)
        s = model.PhotoSet.select(model.PhotoSet.q.name == name)[0]
        return dict(photoset = s, ibox = ibox, mochikit = mochikit, photo_form = photo_form, user = user)

    @expose(template="engal.templates.standardform")
    def saveTagsError(self, user, photo_id, tags, return_url, *args, **kw):
        return dict(form=tag_form, form_action=turbogears.url('/gallery/%s/saveTags' % (user.user_name,)), form_values={})

    #@identity.require(identity.not_anonymous())
    @expose_resource
    @expose()
    @validate(form=tag_form)
    @error_handler(saveTagsError)
    def saveTags(self, user, photo_id, tags, return_url, *args, **kw):
        log.info("args are: %s" % (str(args),))
        log.info("kw are: %s" % (str(kw),))
        log.info("photo_id is: %s" % (str(photo_id),))
        log.info("tags are: %s" % (str(tags),))

        photo = model.Photo.get(photo_id)

        if tags:
            tags = [model.Tag.get(t) for t in tags.values() if t]
            for tag in tags:
                photo.addTag(tag)
        
        raise redirect(return_url)
        return "saveTags"

    @expose_resource
    @expose(template="engal.templates.photo")
    def images(self, user, image_name, *args, **kw):
        log.info(cherrypy.request)
        log.info(dir(cherrypy.request))
        return_url = cherrypy.request.browserUrl
        if not image_name:
            raise NotFound
        photo = model.Photo.byName(image_name)
        user = photo.owner
        photoset = None
        for arg in args:
            if arg.startswith('set-'):
                try:
                    photoset_name = arg[4:]
                    print photoset_name
                    photoset = model.PhotoSet.select(model.PhotoSet.q.name == photoset_name)[0]
                except:
                    pass
                break

        #photoset = kw.get('photoset', None)
        #if photoset:
        #    photoset = model.PhotoSet.select(model.PhotoSet.q.name == photoset)[0]
        #if not photoset:
        #    photoset = photo.sets
        #print "Photoset is:",
        if not photoset:
            if photo.sets:
                photoset = photo.sets[0]
        
        return dict(photo = photo, user = user, ibox = ibox, photoset =
            photoset, editphoto_form = editphoto_form, tag_form =
            tag_form, return_url = return_url, taginfo = TagInfo(photo.taginfo))
