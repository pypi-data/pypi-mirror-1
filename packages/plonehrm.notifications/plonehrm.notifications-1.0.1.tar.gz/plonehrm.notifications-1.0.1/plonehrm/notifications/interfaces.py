from zope.interface import Interface
from zope.annotation.interfaces import IAttributeAnnotatable


class IHRMEmailer(Interface):

    def send():
        """Send an email.
        """


class ICheck(Interface):
    """Browser view for triggering the (daily) checks by modules.
    """


class IHRMModuleEvent(Interface):
    """Event from an HRM module.
    """


class INotified(IAttributeAnnotatable):
    """A warning has already been sent

    Use this for asking if e.g. a warning has already been sent about
    a Contract that has almost ended.
    """

    def has_notification(text):
        """Is text in the notifications?

        In other words: did we already get a notification with this
        text?
        """

    def add_notification(text):
        """Add text to the notifications of this object.

        It is suggested to use this template:

        u'modulename: Notification text'

        So for example:

        u'plonehrm.contracts: Expiry notification'
        """
