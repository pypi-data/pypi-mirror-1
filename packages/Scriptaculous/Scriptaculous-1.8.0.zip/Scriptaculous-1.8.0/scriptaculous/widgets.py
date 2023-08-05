import pkg_resources

from turbogears.widgets import JSLink, Widget, WidgetDescription, \
                               register_static_directory

js_dir = pkg_resources.resource_filename("scriptaculous",
                                         "static/javascript")
register_static_directory("scriptaculous", js_dir)

prototype = JSLink("scriptaculous", "prototype.js") #backward compatibility
prototype_js = JSLink("scriptaculous", "prototype.js")
scriptaculous_js = JSLink("scriptaculous", "scriptaculous.js")

builder_js = JSLink("scriptaculous", "builder.js")
controls_js = JSLink("scriptaculous", "controls.js")
dragdrop_js = JSLink("scriptaculous", "dragdrop.js")
effects_js = JSLink("scriptaculous", "effects.js")
slider_js = JSLink("scriptaculous", "slider.js")
sound_js = JSLink("scriptaculous", "sound.js")
unittest_js = JSLink("scriptaculous", "unittest.js")

class Scriptaculous(Widget):
    """Provides an easy way to use Scriptaculous in your own packages.
    from scriptaculous import scriptaculous, and then just return
    that scriptaculous widget in the output dictionary from your
    controller."""
    javascript = [prototype_js, scriptaculous_js]

scriptaculous = Scriptaculous()

class ScriptaculousDesc(WidgetDescription):
    for_widget = scriptaculous
    template = """<div onclick="new Effect.BlindUp(this)">
      Click here to watch this disappear!
    </div>
    """
    show_separately = True
