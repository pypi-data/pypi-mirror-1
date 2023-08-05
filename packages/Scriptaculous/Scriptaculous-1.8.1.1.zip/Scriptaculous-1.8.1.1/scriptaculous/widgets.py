import pkg_resources

from turbogears import expose
from turbogears.widgets import JSLink, CSSLink, Widget, WidgetDescription, \
                               TextField, \
                               register_static_directory
from turbogears.widgets.base import CoreWD

js_dir = pkg_resources.resource_filename("scriptaculous", "static/javascript")
register_static_directory("scriptaculous", js_dir)
js_dir = pkg_resources.resource_filename("scriptaculous", "static/css")
register_static_directory("scriptaculous_css", js_dir)

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

autocompletefield_css = CSSLink("scriptaculous_css", "autocomplete.css")

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

class AutoCompleteField(TextField):
    "A standard, single-line text field with Scriptaculous AutoComplete enhancements."
    template        = 'scriptaculous.templates.autocomplete'
    css             = [autocompletefield_css]
    params          = ["attrs", "id", "search_controller", "search_param", "min_chars"]
    params_doc      = {'attrs' : 'Dictionary containing extra (X)HTML attributes for'
                                 ' the input tag',
                       'id'    : 'ID for the entire AutoComplete construct.'}
    attrs           = {}
    id              = 'noid'
    search_param    = 'input'
    min_chars       = 2
    javascript      = [prototype_js, scriptaculous_js]

class AutoCompleteFieldDesc(CoreWD):
    name = "Scriptaculous Auto Complete"
    show_separately = True

    template = """
    <div>
        Please choose a country:<br/>
        ${for_widget.display()}
    </div>
    """
    full_class_name = "scriptaculous.widgets.AutoCompleteField"

    def __init__(self, *args, **kw):
        super(AutoCompleteFieldDesc, self).__init__(*args, **kw)
        self.for_widget = AutoCompleteField(
            name="country",
            id="country",
            search_controller="%s/search_for_country" % self.full_class_name,
            search_param="input",
        )

    def ret_as_ul(self, lst):
        if len(lst) == 0:
            return '<ul></ul>'
        else:
            tmp = '</li><li>'.join(lst)
            return '<ul><li>'+tmp+'</li></ul>'

    @expose()
    def search_for_country(self, input):
        from turbogears.i18n import format as tgformat
        input = input.lower()
        found = [country for code, country in tgformat.get_countries() \
                 if input in country.lower()]
        return self.ret_as_ul(found)
