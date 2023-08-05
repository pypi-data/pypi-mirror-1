import pkg_resources
from turbogears import widgets, mochikit

from turbogears.widgets import register_static_directory, JSLink, WidgetDescription
from cherrypy import request
    
js_dir = pkg_resources.resource_filename("xcbl",
                                         "static/javascript")
register_static_directory("xcbl", js_dir)
xcbl_js = JSLink("xcbl", "xcbl.js")
    
__all__ = ['ExtensibleCheckBoxList']

class ExtensibleCheckBoxList(widgets.CheckBoxList):
    '''A CheckBoxList with an 'Other:' option that accepts hand-entered list items.'''
    javascript=[mochikit, xcbl_js]    
    template = """
    <div xmlns:py="http://purl.org/kid/ns#">
        <script type="text/javascript">
            function init_${field_id} (event)
            {
                MochiKit.Signal.connect("${field_id}_txtEntry", 'onchange', otherEntered);
            }
            MochiKit.Signal.connect(window, 'onload', init_${field_id});        
        </script>
        
        <ul
            class="${field_class}"
            id="${field_id}"
            py:attrs="list_attrs"
        >
            <li py:for="value, desc, attrs in options">
                <input type="checkbox"
                    name="${name}"
                    id="${field_id}_${value}"
                    value="${value}"
                    py:attrs="attrs"
                />
                <label for="${field_id}_${value}" py:content="desc" />
            </li>
            <li id="${field_id}_other_listitem">
                <input type="checkbox"
                    name="${name}"
                    id="${field_id}_other"
                    value="other"
                    style="display:none"
                />
                <label for="${field_id}_other"
                    class="fieldlabel">
                    Other:
                </label>
                <input type="text"
                    checkBoxListName="${name}"
                    checkBoxListId="${field_id}"
                    id="${field_id}_txtEntry"            
                    name="${field_id}_txtEntry"
                    insert_before="${field_id}_other_listitem"
                />
            </li>
        </ul>
    </div>"""
    def persistingopts(self):
        try:
            selected = request.params.get(self._name)
        except AttributeError: #no request yet made
            return []
        if type(selected) in (str, unicode):
            return [selected]
        return selected or []
    def __init__(self, *args, **kwargs):
        opts = kwargs['options']
        if callable(opts):
            def myOptions():
                result = opts()
                return result + [x for x in self.persistingopts() if x not in result]
        else:
            def myOptions():
                return opts + [x for x in self.persistingopts() if x not in opts]
        kwargs['options'] = myOptions
            
        super(widgets.CheckBoxList, self).__init__(*args, **kwargs)
        
class ExtensibleCheckBoxListDesc(WidgetDescription):
    name = "Extensible CheckBox List"
    for_widget = ExtensibleCheckBoxList("your_extensible_checkbox_list", 
                              options=[(1, "Python"), 
                                       (2, "Java"), 
                                       (3, "Pascal"),
                                       (4, "Ruby")],
                              default=[1,4])