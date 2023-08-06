from zope.event import notify
from Products.Five import BrowserView

from plonehrm.notifications.events import HRMCheckEvent


class CheckView(BrowserView):
    """View to be called daily from a cronjob, triggers full HRM check.
    """

    def __call__(self):
        notify(HRMCheckEvent(self.context))
        return u'HRMCheckEvent triggered'
