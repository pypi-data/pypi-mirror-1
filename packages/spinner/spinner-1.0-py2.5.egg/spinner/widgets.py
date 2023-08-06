import pkg_resources

from turbogears.widgets import CSSLink, JSLink, Widget, WidgetDescription, \
                               register_static_directory
from turbogears.widgets import *
static_dir = pkg_resources.resource_filename("spinner",
                                         "static")
register_static_directory("spinner", static_dir)


class Spinner(FormField):
      """Creates a spinner widget which can be used directly in html"""
      template = """
      <form xmlns:py="http://purl.org/kid/ns#">
      <table cellpadding="0" cellspacing="0" border="0">
      <tr>
      <td rowspan="2"><input type="text" name="number" value="${value}" class="${field_class}" style="width:50px;height:15px;font-weight:bold;" /></td>
<td><input type="button" value=" /\ " onclick="this.form.number.value++;" style="font-size:7px;margin:0;padding:0;width:20px;height:12px;" /></td>
      </tr>
      <tr>
<td><input type="button" value=" \/ " onclick="this.form.number.value--;" style="font-size:7px;margin:0;padding:0;width:20px;height:12px;" /></td>
      </tr>
      </table>
      </form>
      """

class Spinner(WidgetDescription):
    name = "Spinner"
    for_widget = Spinner("spinner", default="10")
    full_class_name = "spinner.Spinner"