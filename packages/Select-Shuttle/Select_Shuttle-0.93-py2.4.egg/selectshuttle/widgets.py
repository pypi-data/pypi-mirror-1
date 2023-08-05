#!/usr/bin/python
# -*- coding: utf-8 -*-

import pkg_resources

from turbogears import widgets
from turbogears.widgets import CSSLink, JSLink, Widget, WidgetDescription, \
                               register_static_directory

js_dir = pkg_resources.resource_filename("selectshuttle",
                                         "static/javascript")
register_static_directory("selectshuttle", js_dir)

class SelectShuttle(widgets.FormField):
    """
    The SelectShuttle widget provides a mechanism for selecting multiple
    values from a list of values by allowing the user to move items between
    two lists.

    On modern browsers you can also double click an item to move it from one
    list to the other.

    After the first "move", all entries will be sorted automatically
    accordingly to its "description" on both lists.

    Take a look at the code for SelectShuttleDesc for an example of how to use
    this widget in your code.
    """

    javascript = [JSLink("selectshuttle", "OptionTransfer.js")]

    template = """
<div xmlns:py='http://purl.org/kid/ns#'>
  <script language="JavaScript">
    var optrans = new OptionTransfer('${name_left}','${name_right}');
    optrans.setAutoSort(true);
  </script>
  <table align='left' width='100%'>
    <?python
      data_right_descs = []
      for data_right_id, data_right_desc in data_right:
          data_right_descs.append(data_right_desc)
    ?>
    <thead>
      <tr>
        <th align="center" py:content='title_left'>Left Options</th>
        <th></th>
        <th align="center" py:content='title_right'>Right Options</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td width="40%" align="center">
          <select name="${name_left}" id="${name_left}_id"
          multiple="True" size="10" ondblclick="optrans.transferRight()">
            <option py:for="data_id, data_desc in value"
              py:if="not data_desc in data_right_descs"
              py:attrs="value=data_id"
              py:content="data_desc">Content</option>
          </select>
        </td>
        <td valign="middle" align="center">
          <input type="button" name="right" value="&gt;&gt;" onclick="optrans.transferRight()" /><br /><br />
          <input type="button" name="right" py:attrs="value=btn_all_right" onclick="optrans.transferAllRight()" /><br /><br />
          <input type="button" name="left" py:attrs="value=btn_all_left" onclick="optrans.transferAllLeft()" /><br /><br />
          <input type="button" name="left" value="&lt;&lt;" onclick="optrans.transferLeft()" />
        </td>
        <td width="40%" align="center">
          <select name="${name_right}" id="${name_right}_id"
          multiple="True" size="10" ondblclick="optrans.transferLeft()">
            <option py:for="data_id, data_desc in value"
              py:if="data_desc in data_right_descs"
              py:attrs="value=data_id"
              py:content="data_desc">Right Content</option>
          </select>
        </td>
      </tr>
    </tbody>
  </table>
  
  <script language="JavaScript">addLoadEvent(optrans.init(${form_reference}))</script>

</div>
"""

    params = ["title_left", "title_right", "name_left", "name_right",
              "data_right", "form_reference", "btn_all_right",
              "btn_all_left"]

    form_reference = 'document.forms[0]'
    btn_all_right = 'All >>'
    btn_all_left = '<< All'


class SelectShuttleDesc(WidgetDescription):
    name = "Select Shuttle"
    
    # All data should be provided as a list of lists, in the form of
    # ["id", "value"]
    data = [[1, 'Option 1'], [2, 'Option 2'], [3, 'Option 3'],
            [4, 'Option 4'], [5, 'Option 5'], [0, 'Option 6']]
    # The same applies to the selected data.
    data_selected = [[5, 'Option 5']]

    # As you can see, you need to display this widget inside a form.  Using a
    # form is mandatory here due to how the underlying JavaScript works.
    template = """
    <div>
      <form id="selectshuttle_demo_form">
        ${for_widget.display(data, data_right = data_selected)}
      </form>
    </div>
    """

    # This isn't needed in your code, it is here just for the template above
    # be shown at the toolbox.
    full_class_name = "selectshuttle.widgets.SelectShuttle"
    params = ['data', 'data_selected']

    def __init__(self, *args, **kw):
        super(SelectShuttleDesc, self).__init__(*args, **kw)
        # Finally, below is how you declare your widget.
        self.for_widget = SelectShuttle(
            name="select_shuttle_demo",
            title_left = "Available options",
            name_left = "select_shuttle_available",
            title_right = "Selected options",
            name_right = "select_shuttle_selected",
            
            # You can override the text for the "move all" buttons here or at
            # display time.  If doing it here, use something like the
            # commented entries below.  If doing it at the template, then just
            # add these two lines as parameters for the 'display' method
            # there.  Note that *here* you can't need to scape "<" as you'll
            # need to do at the template.
            #btn_all_right = _('All >>')
            #btn_all_left = _('<< All')
            
            # If you only have one form on the page, then "form_reference" is
            # not necessary since it will default to the first form on the
            # page.
            form_reference = "document.forms['selectshuttle_demo_form']",
            )
