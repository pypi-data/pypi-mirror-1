import logging

import cherrypy

import turbogears
from turbogears import controllers, expose, validate, redirect
from turbogears import identity, widgets, validators, mochikit
from turbogears import error_handler, flash
from sqlobject.sqlbuilder import AND

import dispatch

from engal import json, model

log = logging.getLogger("engal.controllers")

from engal.ibox.widgets import Ibox
ibox = Ibox()

import os.path
import time

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

class AddUserField(widgets.WidgetsList):
    user_name = widgets.TextField(validator=validators.NotEmpty, label="User name")
    email_address = widgets.TextField(validator=validators.NotEmpty, label="Email address")
    display_name = widgets.TextField(validator=validators.NotEmpty, label="Display name")
    password = widgets.TextField(validator=validators.NotEmpty)

adduser_form = widgets.TableForm(fields=AddUserField(), submit_text="Add User")

class Root(controllers.RootController):
    def __init__(self, *args, **kw):
        super(Root, self).__init__(*args, **kw)
        import tempfile
        self._cacheDir = turbogears.config.get('engal.cache_directory', 'cache/')
        path = os.environ.get('ENGAL_PATH')
        if not path:
            path = os.getcwd()
        if self._cacheDir:
            self._cacheDir = os.path.join(path, self._cacheDir)
            if not os.path.isdir(self._cacheDir):
                self._cacheDir = None
            
        if not self._cacheDir:
            self._cacheDir = tempfile.mkdtemp(prefix="engal-cache")

    @expose(template="engal.templates.frontpage")
    def index(self, tg_errors = None):
        users = model.User.select()
        if not users.count():
            raise redirect("/firstuser")
        if tg_errors:
            flash("There was a problem with the form!")
        return dict(now=time.ctime(), users = users)

    @expose(template="engal.templates.userpage")
    def photos(self, username = None, photoset = None, photo_id = None, photo_name = None, tg_errors = None):
        if not username:
            return self.index(tg_errors = tg_errors)
        if photoset and photo_id:
            return self.photo(photo_id, photoset=photoset,tg_errors = tg_errors)
        if photoset:
            return self.sets(photoset, tg_errors = tg_errors)
        user = model.User.by_user_name(username)
        photosets = model.PhotoSet.select(user == user)
        if tg_errors:
            flash("There was a problem with the form!")
        return dict(now=time.ctime(), photosets = photosets, ibox = ibox, photoset_form = photoset_form, mochikit = mochikit, user = user)


    @expose(template="engal.templates.login")
    def login(self, forward_url=None, previous_url=None, *args, **kw):

        if not identity.current.anonymous \
            and identity.was_login_attempted() \
            and not identity.get_identity_errors():
            raise redirect(forward_url)

        forward_url=None
        previous_url= turbogears.url(cherrypy.request.path)

        if identity.was_login_attempted():
            msg=_("The credentials you supplied were not correct or "
                   "did not grant access to this resource.")
        elif identity.get_identity_errors():
            msg=_("You must provide your credentials before accessing "
                   "this resource.")
        else:
            msg=_("Please log in.")
            forward_url= cherrypy.request.headers.get("Referer", "/")
        cherrypy.response.status=403
        return dict(message=msg, previous_url=previous_url, logging_in=True,
                    original_parameters=cherrypy.request.params,
                    forward_url=forward_url)

    @expose()
    def logout(self):
        identity.current.logout()
        raise redirect("/")

    @expose(template="engal.templates.photosets")
    def sets(self, name, tg_errors = None):
        # user = model.User.by_user_name(username)
        s = model.PhotoSet.select(model.PhotoSet.q.name == name)[0]
        user = s.user
        return dict(photoset = s, ibox = ibox, mochikit = mochikit, photo_form = photo_form, user = user)

    @expose(template="engal.templates.photo")
    def photo(self, photo_id, **kw):
        photo = model.Photo.get(photo_id)
        user = photo.owner
        photoset = kw.get('photoset', None)
        if photoset:
            photoset = model.PhotoSet.select(model.PhotoSet.q.name == photoset)[0]
        if not photoset:
            photoset = photo.photosets
        print "Photoset is:",
        print photoset
        return dict(photo = photo, user = user, ibox = ibox, photoset = photoset, editphoto_form = editphoto_form)

    @expose(template="engal.templates.firstuser")
    def firstuser(self):
        if model.User.select().count() > 0:
            raise redirect("/")
        return dict(adduser_form = adduser_form)

    @expose()
    @validate(form=adduser_form)
    @error_handler(firstuser)
    def firstuser_create(self, user_name, email_address, display_name, password):
        if model.User.select().count() > 0:
            raise redirect("/")
        model.User(user_name = user_name, email_address = email_address, display_name = display_name, password = password)
        raise redirect("/")

    @expose()
    @validate(form=photoset_form)
    @error_handler(index)
    def addPhotoSet(self, name, title, description, return_path):
        user = identity.current.identity().user
        model.PhotoSet(name=name, title=title, description=description, user=user)
        raise redirect(return_path)

    @expose()
    @validate(form=photo_form)
    @error_handler(sets)
    def addPhoto(self, file, name, description, return_path, photoset_id):
        user = identity.current.identity().user
        print dir(file)
        fn = file.filename
        contents = file.file.read()
        photoset = model.PhotoSet.get(photoset_id)
        p = model.Photo(filename=fn, owner=user, name=name, description=description)
        p.contents = contents
        photoset.addPhoto(p)
        raise redirect(return_path)

    @expose()
    @validate(form=editphoto_form)
    def editPhoto(self, photo_id, name, description, return_path):
        p = model.Photo.get(photo_id)
        p.set(name=name, description=description)
        raise redirect("%s/%d/%s" % (return_path, p.id, name))

    @expose(content_type="image/jpeg")
    def image(self, id, *args, **kw):
        import Image
        import cStringIO as StringIO
        photo = model.Photo.get(id)
        im = None
        out = StringIO.StringIO()
        cache = "%d" % (int(id))
        if len(args):
            if args[0] == 'thumbnail':
                args = args[1:]
                if len(args):
                    wh = str(args[0]).split('x')
                    if len(wh) == 1:
                        wh = (wh[0], wh[0])
                    try:
                        thumbnail_size = (int(wh[0]), int(wh[1]))
                    except:
                        pass

                if not thumbnail_size:
                    thumbnail_size = (150, 150)

                cache = cache + "-thumbnail-%dx%d" % thumbnail_size
                v = self._fromCache(photo, cache)
                if v:
                    return v

                im = Image.open(StringIO.StringIO(photo.contents))
                im.thumbnail(thumbnail_size, Image.ANTIALIAS)

            if args[0] == 'thumbnailbox':
                args = args[1:]
                if len(args):
                    try:
                        thumbnailbox_size = int(args[0])
                    except:
                        pass

                if not thumbnailbox_size:
                    thumbnailbox_size = 75

                cache = cache + "-thumbnailbox-%dx%d" % (thumbnailbox_size, thumbnailbox_size)

                v = self._fromCache(photo, cache)
                if v:
                    return v

                im = Image.open(StringIO.StringIO(photo.contents))

                (w, h) = im.size
                if w > h:
                    top, bottom = 0, h
                    left = (w - h) / 2
                    right = w - left
                elif w < h:
                    left, right = 0, w
                    top = (h - w) / 2
                    bottom = h - top
                else:
                    top, bottom = 0, h
                    left, right = 0, w

                cropped_size = right - left
                im = im.transform((cropped_size, cropped_size), Image.EXTENT, (left, top, right, bottom))
                im.thumbnail((thumbnailbox_size, thumbnailbox_size), Image.ANTIALIAS)
        else:
            im = Image.open(StringIO.StringIO(photo.contents))

        im.save(out, 'JPEG')
        self._toCache(photo, cache, out.getvalue())
        return out.getvalue()

    def _fromCache(self, photo, id):
        import os
        fn = os.path.join(self._cacheDir, id)
        if os.path.exists(fn):
            from cherrypy.lib.cptools import serveFile
            from cherrypy.lib import httptools
            from datetime import datetime, timedelta
            dt = photo.created
            td = timedelta(seconds = 3600)
            now = datetime.now()
            # st = os.stat(fn)
            class dummy:
                pass
            st = dummy()
            st.st_mtime = int(dt.strftime("%s"))
            cherrypy.response.headers["Expires"] = httptools.HTTPDate((now + td).timetuple())
            #return file(fn, 'rb').read()
            return serveFile(fn, st)
        return False

    def _toCache(self, photo, id, value):
        fn = os.path.join(self._cacheDir, id)
        file(fn, 'wb').write(value)
        dt = photo.created
        t = time.mktime(dt.timetuple())
        os.utime(fn, (t, t))
