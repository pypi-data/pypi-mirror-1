from zope.interface import Interface


class IBatch(Interface):
    def create():
        """"""
    


class IEmail(Interface):
    def validate(address):
        """Validates the email address"""
    
    def send(sender, recipient, subject, body, cc=[], bcc=[]):
        """Send the message to the address"""
    
    def sendHTML(sender, recipient, subject, messageHTML, images, messagePlainText, cc=[], bcc=[]):
        """Send the HTML message to the address"""
    
