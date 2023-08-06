from Products.CMFPlone.tests.utils import MockMailHost

class DummyMailHost(MockMailHost):
    """ Dummy mail host implementation, inheriting from the one use by Plone tests.
    """
    
    def _send(self, mfrom, mto, messageText, debug=True):
        """ Implementation of send to also support it.
        """
        # Always called in debug mode.
        result = MockMailHost._send(self, mfrom, mto, messageText, debug=True)
        self.messages.append(result)

