from Products.MailHost.MailHost import MailHost as MailBase
import email

class MockMailHost(MailBase):
    """A MailHost that collects messages instead of sending them.

    Thanks to Rocky Burt for inspiration.
    """
    
    def __init__(self, id):
        MailBase.__init__(self, id)
        self.reset()
    
    def reset(self):
        self.messages = []
    
    def send(self, message, mto=None, mfrom=None, subject=None, encode=None):
        """
        Basically construct an email.Message from the given params to make sure
        everything is ok and store the results in the messages instance var.
        """

        message = email.message_from_string(message)
        message['To'] = mto
        message['From'] = mfrom
        message['Subject'] = subject
        
        self.messages.append(message)
        self._p_changed = True

    def secureSend(self, text, send_to_address, envelope_from, subject, subtype, charset, debug, From):
        message = email.message_from_string(text)
        message['To'] = send_to_address
        message['From'] = From
        message['EnvelopeFrom'] = envelope_from
        message['Subject'] = subject
        message['Subtype'] = subtype
        message['Charset'] = charset
        
        self.messages.append(message)
        self._p_changed = True
        
    def validateSingleEmailAddress(self, address):
        return True # why not
