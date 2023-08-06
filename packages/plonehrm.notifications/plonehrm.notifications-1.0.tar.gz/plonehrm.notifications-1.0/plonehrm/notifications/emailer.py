import logging
from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import parseaddr, formataddr
from zope.i18n import translate
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from interfaces import IHRMEmailer
from Acquisition import Explicit

log = logging.getLogger("plonehrm notifications:")


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
            #    log.warn("Not passing options to template as it "
            #             "is not a dict: %r" % self.options)
            message = self.template()
        return message

    def send(self):
        """Send an email.

        This takes some hints from
        http://mg.pov.lt/blog/unicode-emails-in-python.html

        The charset of the email will be the first one out of
        US-ASCII, ISO-8859-1 and UTF-8 that can represent all the
        characters occurring in the email.
        """
        # First some checks.
        if self.template is None:
            log.error("No template defined.  Please fix.")
            return
        if not self.recipients:
            log.warn("No recipients to send the mail to, not sending.")
            return


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
        sender_name = str(Header(unicode(sender_name), header_charset))
        # Make sure email addresses do not contain non-ASCII characters
        sender_addr = sender_addr.encode('ascii')
        email_from = formataddr((sender_name, sender_addr))

        # Same for the list of recipients.
        recipients = []
        for recipient in self.recipients:
            # Split real name (which is optional) and email address parts
            recipient_name, recipient_addr = parseaddr(recipient)
            recipient_name = str(Header(unicode(recipient_name),
                                        header_charset))
            recipient_addr = recipient_addr.encode('ascii')
            formatted = formataddr((recipient_name, recipient_addr))
            recipients.append(formatted)

        # Translate the subject.
        subject = translate(self.subject, target_language=self.language)
        # Make it a nice header
        subject = Header(unicode(subject), header_charset)

        """
        For testing...
        recipients = [formataddr(('Maurits van Rees',
                                  'maurits@vanrees.org')),
                      formataddr(('Maurits van Rees 2',
                                  'maurits+2@vanrees.org'))]
        """

        email_to = ', '.join(recipients)

        # Create the message ('plain' stands for Content-Type: text/plain)
        msg = MIMEText(message.encode(body_charset), 'plain', body_charset)
        msg['From'] = email_from
        msg['To'] = email_to
        msg['Subject'] = subject
        msg = msg.as_string()

        # Finally send it out.
        mailhost = getToolByName(self.portal, 'MailHost')
        try:
            log.info("Begin sending email to %r " % recipients)
            log.info("Subject: %s " % subject)
            mailhost.send(message=msg)
        except Exception, exc:
            log.error("Failed sending email to %r" % recipients)
            log.error("Reason: %s: %r" % (exc.__class__.__name__, str(exc)))
        else:
            log.info("Succesfully sent email to %r" % recipients)
