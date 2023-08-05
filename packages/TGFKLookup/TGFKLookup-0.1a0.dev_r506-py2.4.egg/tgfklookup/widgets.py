import pkg_resources

from turbogears.widgets import CSSLink, JSLink, Widget, WidgetDescription, \
                               register_static_directory, FormField
from turbogears import expose

from turbojson import jsonify

from scriptaculous import prototype_js

static = pkg_resources.resource_filename("tgfklookup", "static")
register_static_directory("tgfklookup", static)
js_dir = 'tgfklookup/javascript'
images_dir = 'tgfklookup/images'
css_dir = 'tgfklookup/css'

class AutoCompletingFKLookupField(FormField):
    # todo, remove only_suggest
    # cleanup javascript
    """Similar to AutoCompleteField, but it allows lookup from IDs and text"""
    template = """
    <div xmlns:py="http://purl.org/kid/ns#">
        <input type="text" name="${name}" class="${field_class}"
               id="${field_id}" value="${value}" py:attrs="attrs"/>
        
        <input type="text" class="${field_class}" id="${field_id}_text"
               value="" py:attrs="text_field_attrs" />
        
        <img id="${field_id}_spinner" style="display: none"
             src="${tg.url([tg.widgets, 'tgfklookup/images/spinner.gif'])}"/>
        
        <div id="${field_id}_results" class="autoTextResults"></div>
        
        <div py:if="add_link" class="autoTextLink">
            <a href="${add_link}" py:attrs="add_link_attrs">
                ${add_link_text or 'Add'}
            </a>
        </div>
        
        <script type="text/javascript">
            Event.observe(window, 'load', function() {
                // make it global
                window.${field_id}_manager = 
                    new AutoCompletingFKLookupManager('${field_id}', 
                                                      ${options});
            });
        </script>
        
    </div>
    """
    
    javascript = [prototype_js, JSLink(js_dir, 'autocompletingfklookup.js')]
    css = [CSSLink(css_dir, 'autocompletefield.css')]
    params = ['search_controller', 'id_search_param', 'text_search_param', 
              'var_name', 'attrs', 'text_field_attrs', 'id_result_attr',
              'text_result_attr', 'add_link_attrs', 'add_link',
              'add_link_text', 'on_select', 'before_search']
    attrs = {'size': 4}
    text_field_attrs = {}
    add_link_attrs = {}
    add_link = ''
    add_link_text = ''
    
    search_controller = ''
    text_search_param = 'description'
    id_search_param = 'id'
    id_result_attr = 0
    text_result_attr = 1
    var_name = 'items'
    on_select = ''
    before_search = ''
    
    params_doc = {
        'search_controller': 'URL of the controller returning the data',
        'id_search_param': 'Parameter for the controller that will receive '
                           'searchs by ID',
        'text_search_param': 'Parameter for the controller that will receive '
                             'searchs by text',
        'id_result_attr': 'Attribute or index of the results that contain the '
                          'id',
        'text_result_attr': 'Attribute or index of the results that contain '
                            'the text representation',
        'var_name': 'Name of the variable returned from the controller that '
                    'contains the list of results'}
    
    def update_params(self, d):
        super(AutoCompletingFKLookupField, self).update_params(d)
        options = dict()
        options['search_controller'] = d.get('search_controller')
        options['id_search_param'] = d.get('id_search_param')
        options['text_search_param'] = d.get('text_search_param')
        options['id_result_attr'] = d.get('id_result_attr')
        options['text_result_attr'] = d.get('text_result_attr')
        options['var_name'] = d.get('var_name')
        options['on_select'] = d.get('on_select')
        options['before_search'] = d.get('before_search')
        d['options'] = jsonify.encode(options)
    
class AutoCompletingFKLookupFieldDesc(WidgetDescription):
    name = "Auto Completing FK Lookup"
    
    template = """
    <div>
        ${for_widget.display()}
    </div>
    """
    full_class_name = "tgfklookup.widgets.AutoCompletingFKLookupField"
    
    def __init__(self, *args, **kw):
        super(AutoCompletingFKLookupFieldDesc, self).__init__(*args, **kw)
        self.for_widget = \
            AutoCompletingFKLookupField(
                name='person',
                search_controller='%s/search' % self.full_class_name,
                id_search_param='person_id',
                text_search_param='person_name',
                var_name='persons')
        self.example_list = []
        self.example_list.append((1, 'John Doe'))
        self.example_list.append((2, 'Jane Doe'))
        self.example_list.append((3, 'John Smith'))
    
    @expose(format='json')
    def search(self, person_id=None, person_name=None):
        persons = []
        if person_name:
            for person in self.example_list:
                if person_name.lower() in person[1].lower():
                    persons.append(person)
        else:
            try:
                persons.append(self.example_list[int(person_id) - 1])
            except IndexError:
                pass
            except ValueError:
                pass
        return dict(persons=persons)

