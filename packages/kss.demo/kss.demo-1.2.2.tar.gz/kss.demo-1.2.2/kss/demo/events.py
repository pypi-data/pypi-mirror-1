
import zope.component
from zope.component.interfaces import (
    IUtilityRegistration,
    IRegistrationEvent,
    )
from interfaces import (
    IKSSDemoResource,
    IKSSSeleniumTestResource,
    IKSSDemoRegistrationEvent,
    )
from zope.interface import implements

class KSSDemoRegistrationEvent(object):
    """Redispatch of registration for demo utilities"""
    implements(IKSSDemoRegistrationEvent)

@zope.component.adapter(IUtilityRegistration, IRegistrationEvent)
def dispatchRegistration(registration, event):
    """When a demo utility is registered, add it to the registry.
    When a demo utility is registered,  
    event handler registered for the particular component registered,
    the registration and the event.
    """
    component = registration.component
    # Only dispatch registration of the interesting utilities.
    new_event = KSSDemoRegistrationEvent()
    if IKSSDemoResource.providedBy(component) or \
            IKSSSeleniumTestResource.providedBy(component):
        handlers = zope.component.subscribers((component, registration, event, new_event), None)
        for handler in handlers:
            pass # getting them does the work
