
from zope import interface

class ITokenSource( interface.Interface ):

    """
    A session source is an object which creates a session identified and
    can verify if session is still valid.
    """

    def createIdentifier(userid):
        """
        Return an identifier for a userid. An identifier is a standard python
        string object.
        """

    def verifyIdentifier(identifier):
        """
        Verify if an identity corresponds to a valid session. Returns
        a boolean indicating if the identify is valid.
        """

    def extractUserId(identifier):
        """
        Extract the user id from an identifier.
        """

