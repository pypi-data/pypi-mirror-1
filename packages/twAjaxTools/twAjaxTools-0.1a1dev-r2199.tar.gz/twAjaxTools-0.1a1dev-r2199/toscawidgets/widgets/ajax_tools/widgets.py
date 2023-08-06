from toscawidgets.api import Widget, JSLink, CSSLink, js_function
from toscawidgets.widgets.prototype import prototype_js
from toscawidgets.widgets.forms import TableForm, FormField, SingleSelectField
from extensions import HasControllerMixin
from formencode import Invalid

__all__ = ['AjaxFormMixin', 'AjaxTableForm', 'AutoCompletingFKLookupField',
           'UpdatableSingleSelectField']

common_css = CSSLink(modname=__name__, filename='static/common.css')

ajax_form_js = JSLink(modname=__name__, filename='static/ajax_form.js')

class AjaxFormMixin(Widget):
    """
    Form to do asynchronous requests with file upload support.
    """
    
    javascript = [prototype_js, ajax_form_js]
    
    include_dynamic_js_calls = True
    
    manager = js_function('new AjaxFormManager')
    
    _params = ['ignore_redirects', 'on_success', 'on_complete', 'on_failure',
               'clear_after_submit', 'ignore_flash', 'on_identity_failure',
               'ignore_identity_flash']
    params = _params
    
    ignore_redirects = True
    ignore_redirects__doc = ('If set to False and a redirect is raised on '
                             'the remote controller, it will be followed')
    
    clear_after_submit = True
    clear_after_submit__doct = ('If set to True, the form will be reset after '
                                'a succesful submit')
    
    ignore_flash = False
    ignore_flash__doc = ('If set to False and flash() is called on the '
                         'remote controller, it will open an alert msg window')
    
    ignore_identity_flash = False
    ignore_identity_flash__doc = ('When an identity error ocurrs, an alert '
                                  'window will show the message if this is '
                                  'set to False')
    
    # these events will be evaled/called
    on_success = None
    on_complete = None
    on_failure = None
    on_identity_failure = None
    
    def __init__(self, id=None, parent=None, children=[], **kw):
        super(AjaxFormMixin, self).__init__(id, parent, children, **kw)
    
    def update_params(self, d):
        super(AjaxFormMixin, self).update_params(d)
        
        if not getattr(d, 'id', None):
            raise KeyError('Ajax forms need an id')
        
        options = dict()
        for i in self._params:
            options[i] = d[i]
        
        self.add_call(self.manager(d.id, options))


class AjaxTableForm(TableForm, AjaxFormMixin):
    """
    Exactly as the original TableForm, with the exception that it 
    includes AjaxFormMixin and the template always shows the error
    containers so the javascript part can insert the error text later.
    """
    template = 'genshi:toscawidgets.widgets.ajax_tools.templates.table_form'


auto_complete_js = JSLink(modname=__name__, 
                          filename='static/autocompletingfklookup.js')
auto_complete_css = CSSLink(modname=__name__, 
                            filename='static/autocompletefield.css')

class AutoCompletingFKLookupField(FormField):
    """
    Similar to AutoCompleteField, but it allows lookup from IDs and text.
    Will only return the ID of the selected register.
    Also will try to clear the field if the user writes a non existant ID.
    """
    
    template = 'genshi:toscawidgets.widgets.ajax_tools.templates.' \
               'auto_completing_fk_lookup_field'
    
    javascript = [prototype_js, auto_complete_js]
    css = [auto_complete_css, common_css]
    
    include_dynamic_js_calls = True
    
    manager = js_function('new AutoCompletingFKLookupManager')
    
    _params = ['url', 'id_search_param', 'text_search_param', 
               'var_name', 'attrs', 'text_field_attrs', 'id_result_attr',
               'text_result_attr', 'add_link_attrs', 'add_link',
               'add_link_text', 'on_select', 'on_clear', 'before_search',
               'hide_id_field', 'controller', 'extra_data_result_attr']
    params = _params
    
    attrs = {'size': 4}
    text_field_attrs = {}
    add_link_attrs = {}
    add_link = None
    add_link_text = None
    
    url = None
    controller = None # deprecated
    hide_id_field = False
    text_search_param = 'description'
    id_search_param = 'id'
    id_result_attr = 0
    text_result_attr = 1
    extra_data_result_attr = 2
    var_name = 'items'
    
    # javascript hooks
    on_select = None
    on_clear = None
    before_search = None
    
    url__doc = 'URL of the controller returning the data'
    hide_if_field__doc = 'Hide numeric ID field'
    id_search_param__doc = ('Parameter for the controller that will receive '
                            'searchs by ID')
    text_search_param__doc = ('Parameter for the controller that will receive '
                              'searchs by text')
    id_result_attr__doc = ('Attribute or index of the results that contain '
                           'the id')
    text_result_attr__doc = ('Attribute or index of the results that contain '
                             'the text representation')
    extra_data_result_attr__doc = ('Attribute or index of the results that '
                                   'contain extra data for the result')
    var_name__doc = ('Name of the variable returned from the controller that '
                     'contains the list of results')
    
    def update_params(self, d):
        super(AutoCompletingFKLookupField, self).update_params(d)
        
        if d.controller:
            import warnings
            warnings.warn('Use url instead of controller', DeprecationWarning, 
                           1)
            d.url = d.controller
        
        options = dict()
        for i in self._params:
            options[i] = d[i]
        
        if d.hide_id_field:
            d.attrs['style'] = 'display: none;'
        
        self.add_call(self.manager(d.id, options))


select_field_js = JSLink(modname=__name__, 
                         filename='static/updatingselectfield.js')

class UpdatableSingleSelectField(SingleSelectField, HasControllerMixin):
    """
    It's a select field which options can be updated via a javascript call.
    Developed for a ajaxian page that needs to update it's options when the
    user adds a new item.
    """
    
    template = 'genshi:toscawidgets.widgets.ajax_tools.templates.' \
               'updatable_single_select_field'
    
    javascript = [prototype_js, select_field_js]
    css = [common_css]
    
    include_dynamic_js_calls = True
    
    params = ['filter_params', 'opt_feeder', 'access_control', 
              'add_link_attrs', 'add_link', 'add_link_text']
    
    filter_params = {}
    access_control = None
    add_link_attrs = {}
    add_link = ''
    add_link_text = ''
    
    manager = js_function('new UpdatingSelectFieldManager')
    
    def update_params(self, d):
        super(UpdatableSingleSelectField, self).update_params(d)
        
        options = dict()
        options['controller'] = self.controller_url
        options['filter_params'] = d.filter_params
        
        if self.validator:
            try:
                options['initial_value'] = self.validator.from_python(d.value)
                # if you are looking at this code because the field failed to
                # display during a validation error, your validator probably 
                # fired TypeError or ValueError instead of Invalid as it should.
            except Invalid, e:
                options['initial_value'] = d.value
        else:
            options['initial_value'] = d.value
        
        self.add_call(self.manager(d.id, options))
    
    def controller(self, **kw):
        options = self.opt_feeder(**kw)
        return dict(options=options)


