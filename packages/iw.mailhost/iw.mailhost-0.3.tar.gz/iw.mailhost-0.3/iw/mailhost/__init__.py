import logging
import email.Message
import zope.interface
import zope.component
from zope.sendmail.interfaces import IMailDelivery

log = logging.getLogger('iw.mailhost')

def initialize(context):
    pass

def send(self, sender, recipient, message, debug=False):
    """patch MailHost
    """
    if not isinstance(message, email.Message.Message):
        message = email.message_from_string(message)

    utilities = zope.component.getAllUtilitiesRegisteredFor(IMailDelivery)
    if utilities:
        mailer = utilities[0]
        if len(utilities) > 1:
            log.warn('More than one IMailDelivery found. Using %r' % mailer)
        mailer.send(sender, [recipient], message)
    else:
        self._old_send(sender, recipient, message)

# Patch
try:
    import Products.MailHost.MailHost
except ImportError:
    log.error("You don't have MailHost installed")
else:
    if not getattr(Products.MailHost.MailHost.MailHost, '_old_send', None):
        log.info('Patching MailHost')
        Products.MailHost.MailHost.MailHost._old_send = \
                     Products.MailHost.MailHost.MailHost._send
        Products.MailHost.MailHost.MailHost._send = send
try:
    import Products.SecureMailHost.SecureMailHost
except ImportError:
    log.error("You don't have SecureMailHost installed")
else:
    if not getattr(Products.SecureMailHost.SecureMailHost.SecureMailHost,
                                                            '_old_send', None):
        log.info('Patching SecureMailHost')
        Products.SecureMailHost.SecureMailHost.SecureMailHost._old_send = \
                     Products.SecureMailHost.SecureMailHost.SecureMailHost._send
        Products.SecureMailHost.SecureMailHost.SecureMailHost._send = send
