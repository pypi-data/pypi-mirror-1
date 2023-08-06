from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from quintagroup.plonegooglesitemaps import qPloneGoogleSitemapsMessageFactory as _

# -*- extra stuff goes here -*-

class ISitemap(Interface):
    """Search engine Sitemap content type"""

try:
    from Products.DCWorkflow.interfaces import IAfterTransitionEvent
except ImportError:
    # Copy IAfterTransitionEvent from Plone-3/Products.DCWorkflow.interfaces
    from zope.interface import Interface, Attribute
    from zope.app.event.interfaces import IObjectEvent

    class ITransitionEvent(IObjectEvent):
        """An event that's fired upon a workflow transition.
        """

        workflow = Attribute(u"The workflow definition triggering the transition")
        old_state = Attribute(u"The state definition of the workflow state before the transition")
        new_state = Attribute(u"The state definition of the workflow state before after transition")
        transition = Attribute(u"The transition definition taking place. "
                                "May be None if this is the 'transition' to the initial state.")
        status = Attribute(u"The status dict of the object.")
        kwargs = Attribute(u"Any keyword arguments passed to doActionFor() when the transition was invoked")

    class IAfterTransitionEvent(ITransitionEvent):

        """An event that's fired after a workflow transition.
        """
