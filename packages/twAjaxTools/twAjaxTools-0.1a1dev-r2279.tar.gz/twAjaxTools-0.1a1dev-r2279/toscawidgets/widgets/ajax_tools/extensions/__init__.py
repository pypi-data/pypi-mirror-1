import itertools
import dispatch
from toscawidgets.api import Widget
from weakref import WeakValueDictionary, WeakKeyDictionary

__all__ = ['HasControllerMixin']

"""
The idea is to add here what would mediate between framworks and the widgets, 
allowing us to develop controller oriented widgets in a framework agnostic
way.
"""

controller_counter = itertools.count()
controller_prefix = 'ajax_tools_controller'
controllers_locked = False
controllers = WeakKeyDictionary()

class HasControllerMixin(Widget):
    '''
    Mixin to add controller capabilities to the widget
    '''
    
    # the url will be set automatically by the framework implementation
    controller_url = None 
    controller_name = None
    has_controller = True
    access_control_function = None
    
    def __init__(self, *args, **kw):
        '''
        Looks like that TW makes new instances of widgets when they are 
        passed around (from a WidgetsList to a Form for example) and those
        are never desreferenced so a weak reference won't make them to 
        dissapear.
        This makes that every copy of the widget create its own controller.
        Checking if the id is set and making the controller dictionary a 
        WeakValueDictionary only leaves the desired widget there.
        '''
        super(HasControllerMixin, self).__init__(*args, **kw)
        
        if controllers_locked:
            raise 'This object cannot be instantiated during a request'
        
        if not self.id:
            return
        
        self.controller_name = controller_prefix + '_' + \
                                str(controller_counter.next())
        
        controllers[self] = self.controller_name

