from datetime import datetime

from sqlobject import *
#from sqlobject.index import DatabaseIndex

from turbogears import identity 
from turbogears.database import PackageHub
import turbogears.config

hub = PackageHub("engal")
__connection__ = hub

import random
import os.path

from engal.identitymodel import *
from engal.util import getTagIconDirectory

class Photo(SQLObject):
    owner = ForeignKey('User')
    filename = UnicodeCol(length = 255)
    created = DateTimeCol(default = datetime.now)
    sets = SQLRelatedJoin('PhotoSet')
    tags = RelatedJoin('Tag')
    name = UnicodeCol(length = 25, alternateID = True)
    description = UnicodeCol()

    filename_idx = DatabaseIndex("filename")
    owner_idx = DatabaseIndex("owner")

    def imageFilename(self):
        path = os.environ.get('ENGAL_PATH')
        if not path:
            path = os.getcwd()
        base = turbogears.config.get('engal.image_directory', 'images/')
        return os.path.join(path, base, str(self.id))

    def _get_contents(self):
        if not os.path.exists(self.imageFilename()):
            return None
        f = open(self.imageFilename())
        v = f.read()
        f.close()
        return v

    def _set_contents(self, value):
        # assume we get a string for the image
        f = open(self.imageFilename(), 'w')
        f.write(value)
        f.close()

    def _del_contents(self, value):
        os.unlink(self.imageFilename())

    def _get_taginfo(self):
        taginfo = {}
        for tag in self.tags:
            taginfo.setdefault(tag.aspect, [])
            taginfo[tag.aspect].append(tag)

        return taginfo.items()

class PhotoSet(SQLObject):
    name = UnicodeCol(length = 255)
    title = UnicodeCol(length = 255)
    description = UnicodeCol()
    photos = SQLRelatedJoin('Photo')
    user = ForeignKey('User')
    tags = RelatedJoin('Tag')

    user_idx = DatabaseIndex('user')

    def getRandomPhoto(self):
        return getChoice(self.photos)

    def getRandomPhotos(self, number = 5):
        return getSample(self.photos, number)

class TagAspect(SQLObject):
    short_name = UnicodeCol(length = 25, notNone = True, alternateID = True)
    name = UnicodeCol(length = 255)
    uri = UnicodeCol(length = 255, alternateID = True)
    description = UnicodeCol()
    tags = SQLMultipleJoin('Tag', joinColumn = "aspect_id")

    @classmethod
    def add(self, **kw):
        t = TagAspect(**kw)
        Tag.createAspectRootTag(t)

    def iconFilename(self):
        return os.path.join(getTagIconDirectory(), str(self.id))

    def _get_contents(self):
        if not os.path.exists(self.iconFilename()):
            return None
        f = open(self.iconFilename())
        v = f.read()
        f.close()
        return v

    def hasIcon(self):
        if os.path.exists(self.iconFilename()):
            return True
        return False

    def _set_contents(self, value):
        # assume we get a string for the icon
        f = open(self.iconFilename(), 'w')
        f.write(value)
        f.close()

    def _del_contents(self, value):
        os.unlink(self.iconFilename())

    def _get_rootTag(self):
        return Tag.getRoot(self)
        

class Tag(SQLObject):
    short_name = UnicodeCol(length = 25, notNone = True, alternateID = True)
    name = UnicodeCol(length = 255)
    uri = UnicodeCol(length = 255, default = "")
    description = UnicodeCol()
    aspect = ForeignKey('TagAspect')

    photos = SQLRelatedJoin('Photo')
    photosets = SQLRelatedJoin('PhotoSet')

    parentLocation = ForeignKey('Tag', default = None)
    lft = IntCol(default = None)
    rgt = IntCol(default = None)
    depth = IntCol(default = None)
    childTags = SQLMultipleJoin('Tag', joinColumn = 'parent_location_id')

    @classmethod
    def createAspectRootTag(self, aspect):
        Tag(name=aspect.name, short_name=aspect.short_name,
        description=aspect.description, uri=aspect.uri, aspect=aspect,
        lft=0, rgt=1, depth=0)

    def addChildNode(self, t):
        tnl = Tag.q
        to_update_list = Tag.select(AND(tnl.aspectID == self.aspect.id, OR(tnl.rgt > self.lft, tnl.lft > self.lft)))
        for loc in to_update_list:
            kw = {}
            # print loc.lft, loc.rgt
            if loc.rgt > self.lft:
                kw['rgt'] = loc.rgt + 2
            if loc.lft > self.lft:
                kw['lft'] = loc.lft + 2
            # print "Calling set on id %d with args: %s" % (loc.id, str(kw))
            loc.set(**kw)
            loc.sync()

        t.set(lft = self.lft + 1, rgt = self.lft + 2, depth = self.depth + 1, parentLocation = self)

    @classmethod
    def getRoot(self, aspect):
        return self.select(AND(self.q.depth == 0, self.q.aspectID == aspect.id))[0]

User.sqlmeta.addJoin(SQLMultipleJoin('Photo', joinColumn="owner_id", joinMethodName='photos'))
User.sqlmeta.addJoin(SQLMultipleJoin('PhotoSet', joinColumn="user_id", joinMethodName='photosets'))

class SQLObjectSequence(object):
    cached_length = None

    def __init__(self, resultset):
        self.resultset = resultset

    def __len__(self):
        if not self.cached_length:
            self.cached_length = self.resultset.count()
        return self.cached_length

    def __getattr__(self, name):
        return getattr(self.resultset, name)

    def __iter__(self):
        return self.resultset.__iter__()

    def __getitem__(self, n):
        return self.resultset.__getitem__(n)

def getRandomUsers(number = 3):
    users = User.select()
    return getSample(users, number)
    

def getSample(population, number):
    population = SQLObjectSequence(population)
    population_size = len(population)
    if number > population_size:
        number = population_size
    return random.sample(population, number)

def getChoice(population):
    population = SQLObjectSequence(population)
    try:
        return random.choice(population)
    except:
        return None
