from zope.interface import implements
from zope.component import adapts
from interfaces import IAttendeeEnumerator, IInvitationAware
from Products.CMFCore.utils import getToolByName
import re


# The following regular expression was obtained from
# Products.validation.validators.BaseValidators

# email re w/o leading '^'
EMAIL_RE = "([0-9a-zA-Z_&.'+-]+!)*[0-9a-zA-Z_&.'+-]+@(([0-9a-zA-Z]([0-9a-zA-Z-]*[0-9a-z-A-Z])?\.)+[a-zA-Z]{2,6}|([0-9]{1,3}\.){3}[0-9]{1,3})$"


def is_valid_email_address(email):
    return re.compile(EMAIL_RE).match(email)

class AttendeeEnumerator(object):
    implements(IAttendeeEnumerator)
    adapts(IInvitationAware)


    def __init__(self, context):
        self.context = context

    def _isUser(self, userid):
        """ Check if a user exists.
        """
        acl_users = getToolByName(self.context, 'acl_users')
        return bool(acl_users.getUser(userid))

    def _getUserAddress(self, userid):
        """ Get the user's fullname.
        """
        acl_users = getToolByName(self.context, 'acl_users')
        user = acl_users.getUser(userid)
        if user:
            return (user.getProperty('fullname'), user.getProperty('email'))
        return None

    def attendees(self):
        emails = []
        attendees = self.context.getAttendees()
        for attendee in attendees:
            # attendee can be one of three things:
            #   * an email address, which is pretty cool
            #   * a user id, which can also be cool
            #   * someone's name, which is not cool.
            if is_valid_email_address(attendee):
                emails.append(attendee)
            elif self._isUser(attendee):
                fullname, email = self._getUserAddress(attendee)
                emails.append('%s <%s>' % (fullname, email))

        return emails

