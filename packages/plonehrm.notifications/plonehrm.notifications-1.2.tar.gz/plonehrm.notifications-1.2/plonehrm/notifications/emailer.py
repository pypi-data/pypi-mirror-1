import logging
from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import parseaddr, formataddr
import socket

from zope.i18n import translate
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Acquisition import Explicit

from interfaces import IHRMEmailer

logger = logging.getLogger("plonehrm notifications:")


class HRMEmailer(Explicit):
    """Base emailer to send out emails on notifications.

    # Use self.context.users_with_local_role(role)?
    """

    debug_count = 0
    implements(IHRMEmailer)

    def __init__(self, context, template=None, options=None, recipients=None,
                 subject='Notification'):
        self.context = context
        self.template = template
        self.options = options
        self.recipients = recipients
        self.subject = subject

    @property
    def portal(self):
        urltool = getToolByName(self.context, 'portal_url')
        return urltool.getPortalObject()

    @property
    def language(self):
        props = getToolByName(self.portal, 'portal_properties')
        return props.site_properties.getProperty('default_language')

    @property
    def message(self):
        # Use the default site language. Maybe use the language of the user
        # you are sending the email to, if it is known.
        self.context.REQUEST['HTTP_ACCEPT_LANGUAGE'] = self.language
        if isinstance(self.options, dict):
            message = self.template(**self.options)
        else:
            #if self.options != ():
            #    # Apparently an empty dict is no instance of a dict... :(
            #    logger.warn("Not passing options to template as it "
            #             "is not a dict: %r" % self.options)
            message = self.template()
        return message

    @property
    def default_mode(self):
        """ Gets the portal property defining the way mails
        are sent (html or plain).
        """
        portal_props = getToolByName(self.portal,
                                     'portal_properties', None)
        if portal_props is not None:
            hrm_props = getattr(portal_props, 'plonehrm_properties', None)
            if hrm_props is not None:
                if hrm_props.getProperty('html_mails', False):
                    return 'html'

        return 'plain'

    def send(self, mode=''):
        """Send an email.

        This takes some hints from
        http://mg.pov.lt/blog/unicode-emails-in-python.html

        The charset of the email will be the first one out of
        US-ASCII, ISO-8859-1 and UTF-8 that can represent all the
        characters occurring in the email.
        """
        # First some checks.
        if self.template is None:
            logger.error("No template defined.  Please fix.")
            return
        if not self.recipients:
            logger.warn("No recipients to send the mail to, not sending.")
            return

        if not mode in ['plain', 'html']:
            mode = self.default_mode

        charset = self.portal.getProperty('email_charset', 'ISO-8859-1')
        # Header class is smart enough to try US-ASCII, then the charset we
        # provide, then fall back to UTF-8.
        header_charset = charset

        # We must choose the body charset manually
        for body_charset in 'US-ASCII', charset, 'UTF-8':
            try:
                message = self.message.encode(body_charset)
            except UnicodeError:
                pass
            else:
                break

        # Get the 'From' address.
        sender_name = self.portal.getProperty('email_from_name')
        sender_addr = self.portal.getProperty('email_from_address')

        # We must always pass Unicode strings to Header, otherwise it will
        # use RFC 2047 encoding even on plain ASCII strings.
        sender_name = str(Header(safe_unicode(sender_name), header_charset))
        # Make sure email addresses do not contain non-ASCII characters
        sender_addr = sender_addr.encode('ascii')
        email_from = formataddr((sender_name, sender_addr))

        # Same for the list of recipients.
        recipients = []
        for recipient in self.recipients:
            # Split real name (which is optional) and email address parts
            recipient_name, recipient_addr = parseaddr(recipient)
            recipient_name = str(Header(safe_unicode(recipient_name),
                                        header_charset))
            try:
                recipient_addr = recipient_addr.encode('ascii')
            except UnicodeDecodeError:
                # parseaddr can be fooled
                logger.error("UnicodeDecodeError while parsing address %r - "
                             "Ignoring recipient." % recipient)
            else:
                formatted = formataddr((recipient_name, recipient_addr))
                recipients.append(formatted)

        # Translate the subject.
        subject = translate(self.subject, target_language=self.language)
        # Make it a nice header
        subject = Header(safe_unicode(subject), header_charset)

        """
        For testing...
        recipients = [formataddr(('Maurits van Rees',
                                  'maurits@vanrees.org')),
                      formataddr(('Maurits van Rees 2',
                                  'maurits+2@vanrees.org'))]
        """

        # Extra check on recipients.
        if not recipients:
            logger.warn("No recipients to send the mail to, not sending.")
            return

        email_to = ', '.join(recipients)

        msg = MIMEText(message, mode, body_charset)
        msg['From'] = email_from
        msg['To'] = email_to
        msg['Subject'] = subject
        msg = msg.as_string()

        # Finally send it out.
        mailhost = getToolByName(self.portal, 'MailHost')
        try:
            logger.info("Begin sending email to %r " % recipients)
            logger.info("Subject: %s " % subject)
            mailhost.send(message=msg)
        except socket.error, exc:
            logger.error("Failed sending email to %r" % recipients)
            logger.error("Reason: %s: %r" % (exc.__class__.__name__, str(exc)))
        else:
            logger.info("Succesfully sent email to %r" % recipients)
