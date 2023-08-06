import logging

logger = logging.getLogger('collective.eventinviter')

# generic log method
def log(message, summary='', severity=logging.INFO):
    logger.log(severity, '%s \n%s', summary, message)

from zope.i18nmessageid import MessageFactory
EventInviterFactory = MessageFactory('collective.eventinviter')