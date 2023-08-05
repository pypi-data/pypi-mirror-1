import pkg_resources

from turbogears import startup
from turbogears.widgets import CSSLink, JSLink, Widget, WidgetDescription, \
                               register_static_directory, JSSource, \
                               js_location, set_with_self

static_dir = pkg_resources.resource_filename("engal.ibox", "static")
register_static_directory("ibox", static_dir)

ibox_js = JSLink("ibox", "javascript/ibox.js")
ibox_css = CSSLink("ibox", "css/ibox.css", media="screen")

class Ibox(Widget):
    """Creates a Lightbox photo viewer. The value should be the URL of the
    main image to display."""
    javascript = [ibox_js]
    css = [ibox_css]
    
    params = ["thumb_url", "thumb_width", "thumb_height"]
    params_doc = dict(value="URL of the full-size image",
        thumb_url="URL of the thumbnail",
        thumb_width="Thumbnail width",
        thumb_height="Thumbnail height")
    
    template = """<a href="${value}" rel="ibox?ibox_type=0"><img src="${thumb_url}" width="${thumb_width}" height="${thumb_height}" border="0"/></a>
    """
