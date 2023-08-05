import pkg_resources

from turbogears import expose
from turbogears.widgets import CSSLink, JSLink, Widget, WidgetDescription, \
                               register_static_directory, FormField

js_dir = pkg_resources.resource_filename("multicomplete",
                                         "static/javascript")
register_static_directory("multicomplete", js_dir)

xdbc = JSLink("multicomplete", "xdbc.js")
xWoco = JSLink("multicomplete", "xWoco.js")

class MultiCompleteBase(FormField):
    javascript = [xdbc, xWoco]
    params = ["db_src"]

class MultiCompleteField(MultiCompleteBase):
    """Provides a text field where the words are automatically filled
    in based on the XML file provided at db_src."""
    template = """<div xmlns:py="http://purl.org/kid/ns#"><input xmlns:py="http://purl.org/kid/ns#"
        name="${name}"
        class="${field_class}"
        id="${field_id}"
        py:attrs="attrs"
        value="${value}"
        type="text"
    />
    <script type="text/javascript">
        woco.init("${db_src}", "${field_id}");
    </script>
    </div>
    """
    params = ["attrs", "db_src"]
    attrs = {}

class MultiCompleteTextArea(MultiCompleteBase):
    """Provides a text field where the words are automatically filled
    in based on the XML file provided at db_src."""
    template = """<div xmlns:py="http://purl.org/kid/ns#"><textarea xmlns:py="http://purl.org/kid/ns#"
        name="${name}"
        class="${field_class}"
        id="${field_id}"
        rows="${rows}"
        cols="${cols}"
        py:attrs="attrs"
        py:content="value"
    />
    <script type="text/javascript">
        woco.init("${db_src}", "${field_id}");
    </script>
    </div>
    """
    params = ["attrs", "rows", "cols", "db_src"]
    attrs = {}
    rows = 7
    cols = 50

class MultiCompleteFieldDesc(WidgetDescription):
    full_class_name = "multicomplete.MultiCompleteField"
    
    def __init__(self, *args, **kw):
        super(MultiCompleteFieldDesc, self).__init__(*args, **kw)
        self.for_widget = MultiCompleteField(name="multicomplete",
                                    db_src="%s/data.json" %
                                    self.full_class_name)
    
    [expose("json")]
    def data_json(self):
        return dict(data=['alpha',
         'bravo',
         'charlie',
         'delta',
         'echo',
         'foxtrot',
         'golf',
         'hotel',
         'india',
         'juliet',
         'kilo',
         'lima',
         'mike',
         'november',
         'oscar',
         'papa',
         'quebec',
         'romeo',
         'sierra',
         'tango',
         'uniform',
         'victor',
         'whiskey',
         'xray',
         'yankee',
         'zulu'])
        