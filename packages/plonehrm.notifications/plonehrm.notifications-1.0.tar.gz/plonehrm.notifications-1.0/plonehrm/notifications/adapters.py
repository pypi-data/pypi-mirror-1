from zope.interface import implements
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from plonehrm.notifications.interfaces import INotified


class Notified(object):
    """An adapter for objects that people can be notified about.
    """

    implements(INotified)
    ANNO_KEY = 'plonehrm.notifications'

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(context)
        self.metadata = annotations.get(self.ANNO_KEY, None)
        if self.metadata is None:
            annotations[self.ANNO_KEY] = PersistentDict()
            self.metadata = annotations[self.ANNO_KEY]
            self.metadata['notifications'] = PersistentList()
        self.notifications = self.metadata['notifications']

    def has_notification(self, text):
        return text in self.notifications

    def add_notification(self, text):
        if not self.has_notification(text):
            self.notifications.append(text)
