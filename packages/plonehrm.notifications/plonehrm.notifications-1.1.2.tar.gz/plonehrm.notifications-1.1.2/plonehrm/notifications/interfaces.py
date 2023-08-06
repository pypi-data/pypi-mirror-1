from zope.interface import Interface, Attribute
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

    for_manager = Attribute('Event message is meant for a HRM Manager')
    message = Attribute('Message describing this event')


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

    def remove_notification(text):
        """Remove a notification based on the text given."""

    def remove_notification_set(pattern):
        """Remove all notifications that contain pattern."""
