import itertools
from widgets import prototype_js, scriptaculous_js

from turbogears import expose
from turbogears.widgets import PasswordField, CSSLink, JSLink, JSSource
from turbogears.widgets.base import CompoundWidget, Widget, CoreWD

idcounter = itertools.count()

class PasswordStrengthField(PasswordField):
    "A standard, single-line password field with strength meter."
    template        = 'scriptaculous.templates.password_strength_field'
    css             = [CSSLink("scriptaculous", "css/thirdparty/password_strength.css")]
    javascript      = [prototype_js, scriptaculous_js,
                       JSLink("scriptaculous", "javascript/thirdparty/password_strength.js")]

class PasswordStrengthFieldDesc(CoreWD):
    name = "Scriptaculous Password Strength Field"
    show_separately = True

    template = """
    <div>
        Password:<br/>
        ${for_widget.display()}
    </div>
    """
    full_class_name = "scriptaculous.thirdparty.PasswordStrengthField"

    def __init__(self, *args, **kw):
        super(PasswordStrengthFieldDesc, self).__init__(*args, **kw)
        self.for_widget = PasswordStrengthField(
            label='password'
        )

class Tabber(Widget):
    """This widget includes the tabber js and css into your rendered
    page so you can create tabbed DIVs by assigning them the 'panel' class
    and invoking ProtoTabs() on yout tabSet UL.
    """
    css             = [CSSLink("scriptaculous", "css/thirdparty/tabs.css")]
    javascript      = [prototype_js, scriptaculous_js,
                       JSLink("scriptaculous", "javascript/thirdparty/prototabs.js")]

tabberWidget = Tabber()

class TabberDesc(CoreWD):
    name = "Scriptaculous/Prototabs Tabber"
    show_separately = True

    for_widget = Tabber()
    full_class_name = "scriptaculous.thirdparty.Tabber"
    template = """<div>
	<script>
		Event.observe(window, 'load', function(){
			var tabSet1 = new ProtoTabs('tabSet1', {defaultPanel: 'mytab2', ajaxUrls: {
					mytab3: 'scriptaculous.thirdparty.Tabber/dynamic_tab_content',
				}
			});
		});
	</script>
	<div class="tabs10">
		<ul id="tabSet1">
			<li><a href="#mytab1"><span>static</span></a></li>
			<li><a href="#mytab2"><span>default</span></a></li>
			<li><a href="#mytab3"><span>asynchronous</span></a></li>
		</ul>
	</div>
	<div id="mytab1" class="panel">
		Tab with static content. E.g., from your controller.
	</div>
	<div id="mytab2" class="panel">
		Tab which is shown first. I.e., by definition.
	</div>
	<div id="mytab3" class="panel">
		This gets overriden by the AJAX request beingt invoked each time this one gets selected.
	</div></div>"""

    @expose()
    def dynamic_tab_content(self):
        return "This text has been <em>dynamically</em> loaded by an AJAX request."

class Rating(Widget):
    """This widget includes the unobtrusive CSS based rating widget.
    For a more detailed description please see:
    http://livepipe.net/projects/control_rating/
    """
    css             = [CSSLink("scriptaculous", "css/thirdparty/control.rating.css")]
    javascript      = [prototype_js, scriptaculous_js,
                       JSLink("scriptaculous", "javascript/thirdparty/control.rating.js")]

class RatingDesc(CoreWD):
    name = "Scriptaculous Control.Rating"
    show_separately = True

    for_widget = Rating()
    full_class_name = "scriptaculous.thirdparty.Rating"
    template = """<div>
    <table width="100%" cellpadding="0" cellspacing="0" class="api_table">
		<thead>
			<tr><td width="300">Example</td><td class="right">Options</td></tr>
		</thead>
		<tbody>
			<tr>
				<td><div id="rating_one" class="rating_container">
					<a href="#" class="rating_on"></a>
					<a href="#" class="rating_on"></a>
					<a href="#" class="rating_half"></a>
					<a href="#" class="rating_off"></a>
					<a href="#" class="rating_off"></a>
				</div></td>
				<td class="right">{}</td>
			</tr>
			<tr>
				<td><div id="rating_two" class="rating_container"></div></td>
				<td class="right">{value: 2.4}</td>
			</tr>
			<tr>
				<td><div id="rating_four" class="rating_container"></div></td>
				<td class="right">{value: 4, rated: true}</td>
			</tr>
			<tr>
				<td><div id="rating_five" class="rating_container"></div></td>
				<td class="right">{value: 6, rated: false, max:9}</td>
			</tr>
			<tr>
				<td><div id="rating_six" class="rating_container"></div></td>
				<td class="right">{value: 6, rated: false, min: 3, max: 12, multiple: true, reverse: true}</td>
			</tr>
			<tr>
				<td><div id="rating_seven" class="rating_container"></div><input id="rating_seven_input" value="2" style="width:50px;"/></td>
				<td class="right">{input: 'rating_seven_input', multiple: true}</td>
			</tr>
			<tr>
				<td><div id="rating_eight" class="rating_container"></div>
				<select id="rating_eight_select">
					<option value="1">Bad</option>
					<option value="2">Good</option>
					<option value="3">Great</option>
					<option value="4">Excellent</option>
					<option value="5">Really Excellent</option>
				</select></td>
				<td class="right">{input: 'rating_eight_select', multiple: true}</td>
			</tr>
		</tbody>
	</table>
	<script>
		var rating_one = new Control.Rating('rating_one');
		var rating_two = new Control.Rating('rating_two',{value: 2.4});
		var rating_four = new Control.Rating('rating_four',{value: 4,rated: true});
		var rating_five = new Control.Rating('rating_five',{value: 6,rated: false,max:9});
		var rating_six = new Control.Rating('rating_six',{
			value: 6,
			rated: false,
			min: 3,
			max: 12,
			multiple: true,
			reverse: true
		});
		var rating_seven = new Control.Rating('rating_seven',{
			input: 'rating_seven_input',
			multiple: true
		});
		var rating_eight = new Control.Rating('rating_eight',{
			input: 'rating_eight_select',
			multiple: true
		});

	</script></div>"""

class ModalBox(Widget):
    css             = [CSSLink("scriptaculous", "css/thirdparty/modalbox.css")]
    javascript      = [prototype_js, scriptaculous_js,
                       JSLink("scriptaculous", "javascript/thirdparty/modalbox.js")]

modalbox = ModalBox()

class ModalBoxDesc(CoreWD):
    name = "Scriptaculous ModalBox"
    show_separately = True

    for_widget = modalbox
    full_class_name = "scriptaculous.thirdparty.ModalBox"
    template = """<div>
    <ul>
	<li><a href="javascript:Modalbox.MessageBox.alert('Example Alert', 'Some text as body.')"><code>Modalbox.MessageBox.alert</code></a></li>
	<li><a href="javascript:Modalbox.MessageBox.prompt('Example Prompt', 'Please enter something:', 'nothing', function(btn, value){alert('Button: '+btn+' Value: '+value)})"><code>Modalbox.MessageBox.prompt</code></a></li>
	<li><a href="javascript:Modalbox.MessageBox.confirm('Example Confirm Dialog', 'Are you unsure you are sure?', function(value){alert(value)})"><code>Modalbox.MessageBox.confirm</code></a></li>
    </ul>
    </div>"""

ossdl_js = JSLink("scriptaculous", "javascript/thirdparty/ossdl.js")
ossdl_css = CSSLink("scriptaculous", "css/thirdparty/ossdl.css")

class AJAJForm(Widget):
    css             = [ossdl_css]
    javascript      = [prototype_js, ossdl_js]

ajaj_form = AJAJForm()

class AJAJFormDesc(CoreWD):
    name = "Scriptaculous/OSSDL AJAJForms"
    show_separately = True

    for_widget = ajaj_form
    full_class_name = "scriptaculous.thirdparty.AJAJForm"
    template = """<div>
    <form method="post" action="scriptaculous.thirdparty.AJAJForm/proceed_form" onsubmit="return false;" class="AJAJForm">
	<table>
	    <tr><td class="label"><label for="user_name">${_("Your full name:")}</label></td>
		<td class="field"><input type="text" id="user_name" name="user_name"/></td>
	    </tr>
	    <tr><td class="label"><label for="user_age">${_("Your age:")}</label></td>
		<td class="field"><input type="text" id="user_age" name="user_age"/></td>
	    </tr>
	    <tr>
		<td colspan="2" class="buttons"><input type="submit" name="auth" value="${_('confess')}"/></td>
	    </tr>
	</table>
    </form>
    <script type="text/javascript">
        AJAJForms.decorateForms();
    </script>
    </div>
    """

    @expose("json")
    def proceed_form(self, user_name, user_age):
        import cherrypy
        if user_name != "Monty Python":
            cherrypy.response.status = 400
            return {'fielderrors': {'user_name': _("Your name must be 'Monty Python'!")}}
        return {}

class PaginationBar(Widget):
    css             = [ossdl_css]
    javascript      = [prototype_js, ossdl_js]
    params          = ["attrs"]
    attrs           = {}
    template = """<div xmlns:py="http://purl.org/kid/ns#"><div class="paginationBar" py:attrs="attrs"></div>
    <script type="text/javascript">
	PaginationBar.decoratePagingBars();
    </script></div>
    """

pagination_bar = PaginationBar()

class PaginationBarDesc(CoreWD):
    name = "Scriptaculous/OSSDL Pagination Bar"
    show_separately = True

    for_widget = PaginationBar(attrs={'id': "mybar"})
    full_class_name = "scriptaculous.thirdparty.PaginationBar"
    template = """<div>
    ${for_widget.display()}
    <ul>
	<li><a href="javascript:PaginationBar.lock('mybar')">${_("Lock")}</a></li>
	<li><a href="javascript:PaginationBar.unlock('mybar')">${_("Unlock")}</a></li>
    </ul>
    <script type="text/javascript">
	var bar = "mybar";
	PaginationBar.setMaxPage(bar, 4);
	PaginationBar.decoratedBars[bar].callbackGotoPage = function(page) {alert('callbackGotoPage('+page+')')};
	PaginationBar.decoratedBars[bar].callbackReload = function() {alert('You clicked on reload.')};
    </script></div>
    """

class PagingDataGrid(CompoundWidget):
    css             = [ossdl_css]
    javascript      = [prototype_js, ossdl_js]
    params          = ["attrs", "id", "data_url", "property_url"]
    id              = lambda: "grid_%d" % idcounter.next()
    attrs           = {}
    member_widgets  = ['pbar']
    pbar            = pagination_bar
    template = """
	<div xmlns:py="http://purl.org/kid/ns#" py:strip="">
	<div id="${id}" py:attrs="attrs"></div>
	<script type="text/javascript">
		PagingDataGrid.init('${id}', '${data_url}', '${property_url}');
	</script></div>"""

# Use only in case you will overwrite grid's id!
paging_data_grid = PagingDataGrid()
