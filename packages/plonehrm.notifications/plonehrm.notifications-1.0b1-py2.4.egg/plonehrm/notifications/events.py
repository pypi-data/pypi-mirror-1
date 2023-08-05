from zope.interface import implements
from zope.component.interfaces import ObjectEvent
from Products.plonehrm.interfaces import IHRMCheckEvent


class HRMCheckEvent(ObjectEvent):

    implements(IHRMCheckEvent)
