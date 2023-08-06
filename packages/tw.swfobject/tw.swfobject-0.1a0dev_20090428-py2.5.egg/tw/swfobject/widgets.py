from tw.api import Widget, Link, JSLink, CSSLink, js_function

__all__ = ["SwfObject"]

class SwfObject(Widget):
    """
    This Widget encapsulates the google code swfobject JavaScript library (http://code.google.com/p/swfobject/) for embedding Shockwave Flash content in a standards-friendly manner.

    The current swfobject version packaged with this widget is version 2.1 (http://swfobject.googlecode.com/files/swfobject_2_1.zip)

    Example:
        
        From within your controller, simply instantiate a SwfObject and return this instance to be rendered with your template:
        
        swfobject = SwfObject(swf = "/path/to/mycontent.swf", width = 640, height = 480, flashvars = {"myvar": 0}) 


        From within your template, simplay call the swfobject:
        ${swfobject()}
    """

    javascript = [
        JSLink(modname=__name__, filename='static/swfobject.js', javascript=[])
    ]

    params = {
        "swf": "The URL of the Flash content to embed (required)",
        "width": "The width of the flash object in the generated html (default: 300)",
        "height": "The height of the flash object in the generated html (default: 300)",
        "version": "The Shockwave Flash version required by the Flash content (default: 9.0.0)",
        "xi_swf": "The express install Flash content if version requirements are not met (default: static/expressInstall.swf)",
        "flashvars": "Dictionary of flash variable to pass to the Flash content",
        "objparams": "Dictionary of parameters to the embeded object",
        "script_access": "JavaScript access control: sameDomain, always, never (default: sameDomain)",
        "alternate": "Alternate text to display if Shockwave is not supported",
    }

    embed_swf = js_function("swfobject.embedSWF")

    def __init__(self, **kwargs):
        """Initialize the widget here. The widget's initial state shall be
        determined solely by the arguments passed to this function; two
        widgets initialized with the same args. should behave in *exactly* the
        same way. You should *not* rely on any external source to determine
        initial state."""
        super(SwfObject, self).__init__(**kwargs)

        # Load default parameter values
        if self.version is None:
            self.version = "9.0.0"

        if self.script_access is None:
            self.script_access = "sameDomain"

        if self.alternate is None:
            self.alternate = "Shockwave Flash Version ${version} Required", 

        if self.xi_swf is None:
            self.xi_swf = Link(modname=__name__, filename='static/expressInstall.swf')

        if self.flashvars is None:
            self.flashvars = {}

        if self.objparams is None:
            self.objparams = {}

        # Update the object params with the appropriate AllowScriptAccess restriction
        self.objparams['AllowScriptAccess'] = self.script_access

        # Join alternate text/template data with the necessary div where the flash will be embedded
        self.template = """<div id="${id}">%s</div>""" % self.alternate

    def update_params(self, d):
        """This method is called every time the widget is displayed. It's task
        is to prepare all variables that are sent to the template. Those
        variables can accessed as attributes of d."""
        super(SwfObject, self).update_params(d)
        self.add_call(self.embed_swf(self.swf, self.id, self.width, self.height, self.version, self.xi_swf.link, self.flashvars, self.objparams))

