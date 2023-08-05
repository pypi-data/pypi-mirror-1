from turbogears import controllers, expose
import cherrypy

import logging
log = logging.getLogger("engal.resourcecontroller")

class Resource(controllers.Controller):
    item_getter = None
    friendly_resource_name = None
    exposed_resource = True

    @expose()
    def default(self, *vpath, **params):
        if not vpath:
            return self.index(**params)
        # Make a copy of vpath in a list
        vpath = list(vpath)
        atom = vpath.pop(0)
        
        # See if the first virtual path member is a container action
        method = getattr(self, atom, None)
        if method and getattr(method, "expose_container", False):
            return method(*vpath, **params)
        
        # Not a container action; the URI atom must be an existing ID
        # Coerce the ID to the correct db type
        item = self.item_getter(atom)
        if item is None:
            raise cherrypy.NotFound
        self._addResource(item)

        # There may be further virtual path components.
        # Try to map them to methods in this class.
        if vpath:
            method = getattr(self, vpath[0], None)
            if method and getattr(method, "exposed_resource"):
                return method(item, *vpath[1:], **params)
        
        # No further known vpath components. Call a default handler.
        return self.show(item, *vpath, **params)

    def _addResource(self, item):
        if not getattr(cherrypy.request, "_resourcecontroller", None):
            cherrypy.request._resourcecontroller = dict()
        cherrypy.request._resourcecontroller[self] = item
        if self.friendly_resource_name:
            cherrypy.request._resourcecontroller[friendly_resource_name] = item

    def _getResource(self):
        return cherrypy.request._resourcecontroller.get(self, None)

    def _getResources(self):
        return cherrypy.request._resourcecontroller
        

def expose_resource(func):
    func.exposed = False
    func.exposed_resource = True
    return func
