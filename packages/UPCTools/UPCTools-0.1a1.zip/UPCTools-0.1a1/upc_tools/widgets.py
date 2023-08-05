import pkg_resources

from turbogears.widgets import register_static_directory, TextField, JSLink, \
                               RPC, Button
from turbogears.validators import FancyValidator

from div_dialogs.widgets import DialogBoxLink

static = pkg_resources.resource_filename('upc_tools', 'static')
register_static_directory('upc_tools_static', static)
static = 'upc_tools_static'

class UPCValidator(FancyValidator):
    def _to_python(self, value, state):
        return value
    def _from_python(self, value, state):
        return value

class UPCLookupField(TextField):
    template = """
    <div xmlns:py="http://purl.org/kid/ns#">
        <input type="text" name="${name}" class="${field_class}"
               id="${field_id}" value="${value}" py:attrs="attrs" />
        <span style="font-size: small">
            ${dialog.display(dom_id='%s_dialog' % field_id, on_open='getElement("%s_upc_search").value = getElement("%s").value; getElement("%s_upc_search_button").onclick();' % (field_id, field_id, field_id))}
        </span>
        <div id="${field_id}_dialog" style="position: absolute; visibility: hidden;">
            <div style="padding: 3px">
                <div>
                    <script type="text/javascript">
                        function search_upc_if_enter(e) {
                            if (window.event) {
                                e = window.event;
                            }
                            if (e.keyCode == 13) {
                                button = getElement('${field_id}_upc_search_button');
                                button.onclick();
                                return false;
                            }
                            return true;
                        }
                    </script>
                    UPC <input type="text" id="${field_id}_upc_search" name="tg_random" onkeypress="return search_upc_if_enter(event)" />
                    <input id="${field_id}_upc_search_button" type="button" value="Check" onclick="return ajax_upc_lookup('${field_id}_upc_search', '${field_id}_upc_lookup_results');" />
                </div>
                <div id="${field_id}_upc_lookup_results" style="margin-top: 5px">
                </div>
            </div>
        </div>
    </div>
    """
    
    """
    <div style="padding: 3px">
                <div>${form.display(update='%s_upc_results' % field_id)}</div>
                <div id="${field_id}_upc_results">
                </div>
            </div>"""
    params = ['form', 'dialog']
    javascript = [JSLink(static, 'upc_tools.js')]

    def __init__(self, *args, **kw):
        super(UPCLookupField, self).__init__(*args, **kw)
        
        self.javascript.extend(RPC.javascript)
        
        self.dialog = DialogBoxLink(link_text='Check Online',
                                    title='Online UPC Lookup', height=255)
        self.javascript.extend(self.dialog.javascript)
        self.css.extend(self.dialog.css)
        
        self.validator = UPCValidator()

