import random ; random.seed()
import simplejson
import pkg_resources

from turbogears.widgets import CSSLink, JSLink, Widget
from turbogears.widgets import register_static_directory

js_dir = pkg_resources.resource_filename("turboflot", "static")
register_static_directory("turboflot", js_dir)

class TurboFlot(Widget):
    """
        A TurboGears Flot Widget.
    """
    template = """
      <div xmlns:py="http://purl.org/kid/ns#" id="${id}" 
           style="width:${width};height:${height};">
        <script>
          $(document).ready(function() {
            $.plot($("#${id}"), ${data}, ${options});
          });
        </script>
        <div id="turboflotLabel">
          ${label}
        </div>
      </div>
    """
    params = ["data", "options", "height", "width", "id", "label"]
    params_doc = {
            "data"    : "An array of data series",
            "options" : "Plot options",
            "height"  : "The height of the graph",
            "width"   : "The width of the graph",
            "label"   : "Label for the graph",
            "id"      : "An optional ID for the graph"
    }
    css = [CSSLink('turboflot', 'turboflot.css')]
    javascript = [JSLink('turboflot', 'excanvas.js'),
                  JSLink("turboflot", "jquery.js"),
                  JSLink("turboflot", "jquery.flot.js")]

    def __init__(self, data, options={}, height="300px", width="600px",
                 id=None, label=''):
        super(TurboFlot, self).__init__()
        if id:
            self.id = id
        else:
            self.id = "turboflot" + str(int(random.random() * 1000))
        self.data = simplejson.dumps(data)
        self.options = simplejson.dumps(options)
        self.height = height
        self.width = width
        self.label = label
