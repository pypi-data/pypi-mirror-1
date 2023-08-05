from turbogears.decorator import simple_decorator
from turbogears.controllers import _get_flash
from toscawidgets.api import js_function
import cherrypy

parent_S = js_function('window.parent.$')

@simple_decorator
def ajax_form_connector(func, *args, **kw):
    """
    Transmits the validation status/errors, flash message, redirects and 
    output to the ajax_form that initated the request
    """
    parent_id = kw.pop('_ajax_form_parent_id')
    status = 'OK'
    
    output = None
    redirect = None
    try:
        output = func(*args, **kw)
    except cherrypy.HTTPRedirect, e:
        redirect = e.args[0][0]
    except NotImplementedError, e:
        if 'has no applicable error handler' not in e.args[0]:
            raise
    
    form_errors = None
    if getattr(cherrypy.request, 'validation_errors', None):
        form_errors = cherrypy.request.validation_errors
        status = 'FAILED_VALIDATION'
    
    response = dict(output=output, redirect=redirect, flash=_get_flash(),
                    form_errors=form_errors, status=status)
    
    # this doesn't work
    # callback = parent_S(parent_id).ajax.submitted(response)
    
    # this is a workaround (had to add .get_manager to the form)
    callback = parent_S(parent_id).get_manager().submitted(response)
    
    return '<script type="text/javascript">%s</script>' % callback
    


