import pkg_resources
import itertools
import cherrypy

from turbogears.widgets import CSSLink, JSLink, Widget, WidgetDescription, \
                               register_static_directory, FormField, \
                               SingleSelectField
from turbogears import expose, identity

from turbojson import jsonify

from scriptaculous import prototype_js

instance_counter = itertools.count()
static = pkg_resources.resource_filename("tgfklookup", "static")
register_static_directory("tgfklookup", static)
js_dir = 'tgfklookup/javascript'
images_dir = 'tgfklookup/images'
css_dir = 'tgfklookup/css'

controllers = []
controllers_locked = False

def start_extension():
    controllers_locked = True
    for name, controller in  controllers:
        if hasattr(cherrypy.root, name):
            raise 'Error while attaching controller %s, already exists' % name
        setattr(cherrypy.root, name, controller)

def stop_extension():
    for name, controller in  controllers:
        if not hasattr(cherrypy.root, name):
            raise 'Error while dettaching controller %s, missing' % name
        delattr(cherrypy.root, name)
    controllers_locked = False

class AutoCompletingFKLookupField(FormField):
    # todo, remove only_suggest
    # cleanup javascript
    """Similar to AutoCompleteField, but it allows lookup from IDs and text"""
    template = """
    <div xmlns:py="http://purl.org/kid/ns#">
        <span>
        <input type="text" name="${name}" class="${field_class}"
               id="${field_id}" value="${value}" py:attrs="attrs"/>
        
        <input type="text" class="${field_class}" id="${field_id}_text"
               value="" py:attrs="text_field_attrs" />
        </span>
        
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
                                                      ${manager_options});
            });
        </script>
        
    </div>
    """
    
    javascript = [prototype_js, JSLink(js_dir, 'autocompletingfklookup.js')]
    css = [CSSLink(css_dir, 'autocompletefield.css')]
    params = ['controller', 'id_search_param', 'text_search_param', 
              'var_name', 'attrs', 'text_field_attrs', 'id_result_attr',
              'text_result_attr', 'add_link_attrs', 'add_link',
              'add_link_text', 'on_select', 'on_clear', 'before_search']
    attrs = {'size': 4}
    text_field_attrs = {}
    add_link_attrs = {}
    add_link = ''
    add_link_text = ''
    
    controller = ''
    text_search_param = 'description'
    id_search_param = 'id'
    id_result_attr = 0
    text_result_attr = 1
    var_name = 'items'
    on_select = ''
    on_clear = ''
    before_search = ''
    
    params_doc = {
        'controller': 'URL of the controller returning the data',
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
        options['controller'] = d.get('controller')
        options['id_search_param'] = d.get('id_search_param')
        options['text_search_param'] = d.get('text_search_param')
        options['id_result_attr'] = d.get('id_result_attr')
        options['text_result_attr'] = d.get('text_result_attr')
        options['var_name'] = d.get('var_name')
        options['on_select'] = d.get('on_select')
        options['on_clear'] = d.get('on_clear')
        options['before_search'] = d.get('before_search')
        d['manager_options'] = jsonify.encode(options)
    
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
                controller='%s/search' % self.full_class_name,
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

class UpdatableSingleSelectField(SingleSelectField):
    """It's a select field which options can be updated via a javascript call.
       Developed for a ajaxian page that needs to update it options when the
       user adds a new item."""
    
    template = """
    <div xmlns:py="http://purl.org/kid/ns#">
        <select name="${name}" class="${field_class}" id="${field_id}"
                py:attrs="attrs">
            <option py:for="value, desc, attrs in options"
                value="${value}"
                py:attrs="attrs"
                py:content="desc"
            />
        </select>
        
        <img id="${field_id}_spinner" style="display: none"
             src="${tg.url([tg.widgets, 'tgfklookup/images/spinner.gif'])}"/>
        
        <div py:if="add_link" class="autoTextLink">
            <a href="${add_link}" py:attrs="add_link_attrs">
                ${add_link_text or 'Add'}
            </a>
        </div>
        
        <script type="text/javascript">
            window.${field_id}_manager = 
                new UpdatingSelectFieldManager('${field_id}',
                                               ${manager_options});
        </script>
    </div>
    """
    
    javascript = [prototype_js, JSLink(js_dir, 'updatingselectfield.js')]
    css = [CSSLink(css_dir, 'autocompletefield.css')]
    params = ['filter_params', 'opt_feeder', 'predicate', 'add_link_attrs',
              'add_link', 'add_link_text']
    filter_params = {}
    predicate = None
    add_link_attrs = {}
    add_link = ''
    add_link_text = ''
    
    def __init__(self, *args, **kw):
        super(UpdatableSingleSelectField, self).__init__(*args, **kw)
        if controllers_locked:
            raise 'This object cannot be instantiated during a request'
        self.instance_id = instance_counter.next()
        self.controller_name = 'tgfklookup_%i' % self.instance_id
        if hasattr(cherrypy.root, self.controller_name):
            raise 'Duplicated widget ID?'
        controllers.append((self.controller_name, self.controller))
    
    def update_params(self, d):
        d['options'] = self.opt_feeder()
        super(UpdatableSingleSelectField, self).update_params(d)
        options = dict()
        options['controller'] = '/' + self.controller_name
        d['manager_options'] = jsonify.encode(options)
    
    @expose(format='json')
    def controller(self, *args, **kw):
        if self.predicate:
            errors = []
            if not self.predicate.eval_with_object(identity.current, errors):
                raise identity.IdentityFailure(errors)
        kw.pop('_', None)
        options = self.opt_feeder(**kw)
        return dict(options=options)

