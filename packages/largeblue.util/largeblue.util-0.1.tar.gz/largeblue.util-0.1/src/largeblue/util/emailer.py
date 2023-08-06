import re, logging

import email.MIMEText
import email.MIMEMultipart
import email.MIMEImage
import email.Header
import email.Charset
email.Charset.add_charset('utf-8', email.Charset.SHORTEST, None, None)

from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope.interface import implements
from zope.sendmail.interfaces import IMailDelivery

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("largeblue")

from interfaces import IEmail


find_valid_username = re.compile(r"^[^ \t\n\r@<>()]+$", re.I).search
find_valid_domain = re.compile(r"^[a-z0-9][a-z0-9\.\-_]*\.[a-z]+$", re.I).search


class Invalid(Exception):
    __doc__ = u'Invalid email address'



class Email(object):
    implements(IEmail)
    def validate(self, value):
        value = value.strip()
        if not value:
            raise Invalid(_(u"Please enter an email address."))
        splitted = value.split('@')
        if not len(splitted) == 2:
            raise Invalid(_(u"An email address must contain a single @"))
        if not find_valid_username(splitted[0]):
            raise Invalid("%s %s " % (
                    _(u"The username part of the address is invalid:"),
                    splitted[0]
                )
            )
        if not find_valid_domain(splitted[1]):
            raise Invalid("%s %s " % (
                    _(u"The domain part of the address is invalid:"),
                    splitted[1]
                )
            )
        return value
    
    def send(self, sender, recipient, subject, body, cc=[], bcc=[]):
        msg = email.MIMEText.MIMEText(
            body.encode('UTF-8'), 
            'plain', 
            'UTF-8'
        )
        msg["From"] = self.validate(sender)
        msg["To"] = self.validate(recipient)
        msg["Subject"] = email.Header.Header(subject, 'UTF-8')
        if cc:
            msg["Cc"] = ', '.join(
                [self.validate(item) for item in cc]
            )
        for item in bcc:
           self.validate(item)
        recipients = [recipient] + cc + bcc
        try:
            mailer = getUtility(IMailDelivery, 'largeblue')
            mailer.send(
                sender, 
                recipients, 
                msg.as_string()
            )
        except ComponentLookupError:
            logging.info('no mailer registered to send email to %s' % (
                    ', '.join(recipients)
                )
            )
        
    
    def sendHTML(self, sender, recipient, subject, messageHTML, images, messagePlainText, cc=[], bcc=[]):
        # Create the root message and fill in the from, to, and subject headers
        msgRoot = email.MIMEMultipart.MIMEMultipart('related')
        msgRoot['Subject'] = email.Header.Header(subject, 'UTF-8')
        msgRoot['From'] = self.validate(sender)
        msgRoot['To'] = self.validate(recipient)
        msgRoot.preamble = 'This is a multi-part message in MIME format.'
        # Encapsulate the plain and HTML versions of the message body in an
        # 'alternative' part, so message agents can decide which they want to display.
        msgAlternative = email.MIMEMultipart.MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
        msgText = email.MIMEText.MIMEText(messagePlainText.encode('UTF-8'), 'plain', 'UTF-8')
        msgAlternative.attach(msgText)
        msgText = email.MIMEText.MIMEText(messageHTML.encode('UTF-8'), 'html', 'UTF-8')
        msgAlternative.attach(msgText)
        for image in images:
            fp = open(image['path'], 'rb')
            msgImage = email.MIMEImage.MIMEImage(fp.read())
            fp.close()
            # Define the image's ID as referenced above
            msgImage.add_header('Content-ID', '<%s>' % image['id'])
            msgRoot.attach(msgImage)
        if cc:
            msgRoot["Cc"] = ', '.join(
                [self.validate(item) for item in cc]
            )
        for item in bcc:
           self.validate(item)
        recipients = [recipient] + cc + bcc
        try:
            mailer = getUtility(IMailDelivery, 'largeblue')
            mailer.send(
                sender, 
                recipients, 
                msgRoot.as_string()
            )
        except ComponentLookupError:
            logging.info('no mailer registered to send email to %s' % (
                    ', '.join(recipients)
                )
            )
        
    

