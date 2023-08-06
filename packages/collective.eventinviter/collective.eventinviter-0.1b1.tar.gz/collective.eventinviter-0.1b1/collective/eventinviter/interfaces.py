from zope.interface import Interface

class IInvitationAware(Interface):
    """ Marker interface for invitation aware events.
    """

class IAttendeeEnumerator(Interface):
    """ Adapts IInvitationAware events to retrieve list of attendees to be invited.
    """

    def attendees():
        """ Returns the list of attendees' email addresses.
        """

class IInviter(Interface):
    """ Adapts IInvitationAware events and is responsible for sending invitations to attendees.
    """
    
    def invite():
        """ Send invitation to attendees retrieved by the enumerator.
        """