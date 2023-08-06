from turbogears.decorator import simple_decorator
from turbogears.controllers import _get_flash, expose
from turbogears import config, identity
from toscawidgets.api import js_function
from toscawidgets.widgets.ajax_tools import extensions
import types
import cherrypy

parent_S = js_function('window.parent.$')

def build_response(form, response):
    callback = parent_S(form).ajax.submitted(response)
    return '<script type="text/javascript">%s</script>' % callback

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
    except cherrypy.InternalRedirect, e:
        if isinstance(e, identity.IdentityFailure):
            errors = '\n'.join(identity.get_identity_errors())
            response = dict(status='IDENTITY_FAILURE', identity_flash=errors)
            return build_response(form=parent_id, response=response)
        else:
            raise
    except NotImplementedError, e:
        # catch the error that not having an @error_handler() raises
        if not e.args or 'has no applicable error handler' not in e.args[0]:
            raise
    
    form_errors = None
    if getattr(cherrypy.request, 'validation_errors', None):
        form_errors = cherrypy.request.validation_errors
        status = 'FAILED_VALIDATION'
    
    response = dict(output=output, redirect=redirect, flash=_get_flash(),
                    form_errors=form_errors, status=status)
    
    return build_response(form=parent_id, response=response)

def start_extension():
    if not config.get('toscawidgets.on', False):
        return
    
    extensions.controllers_locked = True
    
    for obj, controller_name in extensions.controllers.iteritems():
        controller_name = obj.controller_name
        if hasattr(cherrypy, controller_name):
            raise '%s already exists in cherrypy.root' % controller
        
        # Had to override the method because TW won't let me modify the widget
        # after the instantiation. 
        # I don't think it thread unsafe to modify it at this point.
        object.__setattr__(obj, 'controller_url', '/' + obj.controller_name)
        
        # Add the needed decorators to the simplified widget controller:
        # identity.require, expose, etc
        controller = obj.controller.im_func
        
        # FIXME: I have to apply this wrapper or for some reason controllers
        # won't return the expected output.
        # I think there's a bug behind this
        @simple_decorator
        def wrapper(func, *args, **kw):
            return func(*args, **kw)
        controller = wrapper(controller)
        
        if obj.access_control_function:
            controller = identity.require(obj.access_control_function)\
                            (controller)
        
        controller = expose(format='json')(controller)
        controller = types.MethodType(controller, obj, obj.__class__)
        object.__setattr__(obj, '_tg_controller', controller)
        
        # Attach it to the app's root
        setattr(cherrypy.root, controller_name, controller)

def shutdown_extension():
    if not config.get('toscawidgets.on', False) or \
       not extensions.controllers_locked:
        return
    
    extensions.controllers_locked = False
    
    for obj, controller_name in extensions.controllers.iteritems():
        if hasattr(cherrypy, controller_name):
            delattr(cherrpy, controller_name)

