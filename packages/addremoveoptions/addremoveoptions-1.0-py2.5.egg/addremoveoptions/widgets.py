import pkg_resources

from turbogears.widgets import CSSLink, JSLink, Widget, WidgetDescription, \
                               register_static_directory
from turbogears.widgets import *
static_dir = pkg_resources.resource_filename("addremoveoptions",
                                         "static")
register_static_directory("addremoveoptions", static_dir)
add_remove_options_js = JSLink("addremoveoptions", "javascript/addremoveoptions.js")


class Addremoveoptions(FormField):
    """Creates a selectbox in which you can add options and remove options"""
    
    template = """
    <form xmlns:py="http://purl.org/kid/ns#">
    <select id="selectX" size="8" multiple="multiple">
    <option value="original1" selected="selected">Original 1</option>
    <option value="original2">Original 2</option>
    </select>
    <br />
    <input type="button" value="Insert Before Selected" onclick="insertOptionBefore(count1++);" /><br />
    <input type="button" value="Remove Selected" onclick="removeOptionSelected();" /><br />
    <input type="button" value="Append Last Entry" onclick="appendOptionLast(count2++);" /><br />
    <input type="button" value="Remove Last Entry" onclick="removeOptionLast();" />
    </form>
 
    """
    def __init__(self,*args, **kw):
        self.javascript = [add_remove_options_js]
        super(Addremoveoptions, self).__init__(*args, **kw) 

class Add_remove_optionsDesc(WidgetDescription):
    name = "Add Remove Options"
    for_widget = Addremoveoptions()
    full_class_name = "addremoveoptions.Addremoveoptions"