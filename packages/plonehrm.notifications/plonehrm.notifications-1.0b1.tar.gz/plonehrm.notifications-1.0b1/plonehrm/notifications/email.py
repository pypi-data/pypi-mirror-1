import logging
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from interfaces import IHRMEmailer
from Acquisition import Explicit

log = logging.getLogger("plonehrm notifications:")


class HRMEmailer(Explicit):
    """Base emailer to send out emails on notifications.

    # Use self.context.users_with_local_role(role)?
    """

    implements(IHRMEmailer)

    def __init__(self, context, template=None, options=None, recipients=None,
                 subject='Notification'):
        self.context = context
        self.template = template
        self.options = options
        self.recipients = recipients
        self.subject = subject
        urltool = getToolByName(self.context, 'portal_url')
        self.portal = urltool.getPortalObject()

    def email_from(self):
        name = self.portal.getProperty('email_from_name')
        address = self.portal.getProperty('email_from_address')
        return "%s <%s>" % (name, address)

    def message(self):
        props = getToolByName(self.portal, 'portal_properties')
        lang = props.site_properties.getProperty('default_language')
        # Use the default site language. Maybe use the language of the user
        # you are sending the email to, if it is known.
        self.context.REQUEST['HTTP_ACCEPT_LANGUAGE'] = lang
        if isinstance(self.options, dict):
            message = self.template(**self.options)
        else:
            #if self.options != ():
            #    # Apparently an empty dict is no instance of a dict... :(
            #    log.warn("Not passing options to template as it "
            #             "is not a dict: %r" % self.options)
            message = self.template()
        return message

    def send(self):
        # First some checks.
        if self.template is None:
            log.error("No template defined.  Please fix.")
            return
        if not self.recipients:
            log.warn("No recipients to send the mail to, not sending.")
            return
        # Then grab the message.
        message = self.message()
        # Finally send it out.
        mailhost = getToolByName(self.portal, 'MailHost')
        try:
            log.debug("Begin sending email to %s " % self.recipients)
            mailhost.send(mto=self.recipients,
                          mfrom=self.email_from(),
                          subject=self.subject,
                          message=message)
        except Exception, exc:
            log.error("Failed sending email to %s" % self.recipients)
            log.error("Reason: %s: %r" % (exc.__class__.__name__, str(exc)))
        else:
            log.info("Succesfully sent email to %s" % self.recipients)
