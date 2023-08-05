import pkg_resources

from turbogears.widgets import JSLink, Widget, WidgetDescription, \
                               register_static_directory

js_dir = pkg_resources.resource_filename("scriptaculous",
                                         "static/javascript")
register_static_directory("scriptaculous", js_dir)

prototype = JSLink("scriptaculous", "prototype.js")
scriptaculous_js = JSLink("scriptaculous", "scriptaculous.js")

class Scriptaculous(Widget):
    """Provides an easy way to use Scriptaculous in your own packages.
    from scriptaculous import scriptaculous, and then just return
    that scriptaculous widget in the output dictionary from your
    controller."""
    javascript = [prototype, scriptaculous_js]

scriptaculous = Scriptaculous()

class ScriptaculousDesc(WidgetDescription):
    for_widget = scriptaculous
    template = """<div onclick="new Effect.BlindUp(this)">
      Click here to watch this disappear!
    </div>
    """
    show_separately = True
    