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

class Photo(SQLObject):
    owner = ForeignKey('User')
    filename = UnicodeCol(length = 255)
    created = DateTimeCol(default = datetime.now)
    sets = SQLRelatedJoin('PhotoSet')
    # contents = BLOBCol()
    tags = RelatedJoin('TagNodeDetails')
    name = UnicodeCol(length = 25)
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

class PhotoSet(SQLObject):
    name = UnicodeCol(length = 255)
    title = UnicodeCol(length = 255)
    description = UnicodeCol()
    photos = SQLRelatedJoin('Photo')
    user = ForeignKey('User')

    user_idx = DatabaseIndex('user')

    def getRandomPhoto(self):
        l = list(self.photos)
        if not l:
            return None
        return random.choice(l)

    def getRandomPhotos(self, number = 5):
        l = list(self.photos)
        if not l:
            return None
        if number > len(l):
            number = len(l)
        return random.sample(l, number)

class TagNodeDetails(SQLObject):
    short_name = UnicodeCol(length = 25)
    name = UnicodeCol(length = 255)
    description = UnicodeCol()
    locations = SQLMultipleJoin('TagNodeLocation', joinColumn = 'node_id')
    photos = SQLRelatedJoin('Photo')

class TagNodeLocation(SQLObject):
    class sqlmeta:
        lazyUpdate = False
    node = ForeignKey('TagNodeDetails', default = None)
    parentLocation = ForeignKey('TagNodeLocation', default = None)
    lft = IntCol(default = None)
    rgt = IntCol(default = None)
    depth = IntCol(default = None)
    childNodes = SQLMultipleJoin('TagNodeLocation', joinColumn = 'parent_location_id')

    def addChildNode(self, t):
        #from sqlobject.sqlbuilder import Update
        #tnl = TagNodeLocation.q
        #u1 = Update(self.sqlmeta.table, {'rgt': tnl.rgt + 2}, where=(tnl.rgt > self.lft))
        #u2 = Update(self.sqlmeta.table, {'lft': tnl.lft + 2}, where=(tnl.lft > self.lft))
        #self._connection.query(str(u1))
        #self._connection.query(str(u2))
        #self._connection.cache.caches[self.__class__.__name__].expireAll()
        #self.sync()
        #t.set(lft = self.lft + 1, rgt = self.lft + 2, depth = self.depth + 1)

        tnl = TagNodeLocation.q
        to_update_list = TagNodeLocation.select(OR(tnl.rgt > self.lft, tnl.lft > self.lft))
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

        t.set(lft = self.lft + 1, rgt = self.lft + 2, depth = self.depth + 1)

    @classmethod
    def getRoot(self):
        return self.select(self.q.depth == 0)[0]

class VisitIdentity(SQLObject):
    visit_key = StringCol( length=40, alternateID=True,
                          alternateMethodName="by_visit_key" )
    user_id = IntCol()


class Group(SQLObject):
    """
    An ultra-simple group definition.
    """
    
    # names like "Group", "Order" and "User" are reserved words in SQL
    # so we set the name to something safe for SQL
    class sqlmeta:
        table="tg_group"
    
    group_name = UnicodeCol( length=16, alternateID=True,
                            alternateMethodName="by_group_name" )
    display_name = UnicodeCol( length=255 )
    created = DateTimeCol( default=datetime.now )

    # collection of all users belonging to this group
    users = RelatedJoin( "User", intermediateTable="user_group",
                        joinColumn="group_id", otherColumn="user_id" )

    # collection of all permissions for this group
    permissions = RelatedJoin( "Permission", joinColumn="group_id", 
                              intermediateTable="group_permission",
                              otherColumn="permission_id" )


class User(SQLObject):
    """
    Reasonably basic User definition. Probably would want additional attributes.
    """
    # names like "Group", "Order" and "User" are reserved words in SQL
    # so we set the name to something safe for SQL
    class sqlmeta:
        table="tg_user"

    user_name = UnicodeCol( length=16, alternateID=True,
                           alternateMethodName="by_user_name" )
    email_address = UnicodeCol( length=255, alternateID=True,
                               alternateMethodName="by_email_address" )
    display_name = UnicodeCol( length=255 )
    password = UnicodeCol( length=40 )
    created = DateTimeCol( default=datetime.now )

    # groups this user belongs to
    groups = RelatedJoin( "Group", intermediateTable="user_group",
                         joinColumn="user_id", otherColumn="group_id" )

    photos = SQLMultipleJoin('Photo', joinColumn="owner_id")
    photosets = SQLMultipleJoin('PhotoSet', joinColumn="user_id")

    def _get_permissions( self ):
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms
        
    def _set_password( self, cleartext_password ):
        "Runs cleartext_password through the hash algorithm before saving."
        hash = identity.encrypt_password(cleartext_password)
        self._SO_set_password(hash)
        
    def set_password_raw( self, password ):
        "Saves the password as-is to the database."
        self._SO_set_password(password)

    def getRandomPhoto(self):
        l = list(self.photos)
        if not l:
            return None
        return random.choice(l)

    def getRandomPhotos(self, number = 5):
        l = list(self.photos)
        if not l:
            return None
        if number > len(l):
            number = len(l)
        return random.sample(l, number)


class Permission(SQLObject):
    permission_name = UnicodeCol( length=16, alternateID=True,
                                 alternateMethodName="by_permission_name" )
    description = UnicodeCol( length=255 )
    
    groups = RelatedJoin( "Group",
                        intermediateTable="group_permission",
                         joinColumn="permission_id", 
                         otherColumn="group_id" )
