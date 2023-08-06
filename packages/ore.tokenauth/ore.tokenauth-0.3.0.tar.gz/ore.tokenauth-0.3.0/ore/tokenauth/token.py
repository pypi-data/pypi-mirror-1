"""
Based Heavily on plone.session by Wichert Akkerman

"""
import hmac, sha

from zope.component import queryUtility
from plone.keyring.interfaces import IKeyManager

from zope import interface
from ore.tokenauth import interfaces

class NoKeyManager(Exception):
    pass

class HashToken( object ):
    """A Hash token source implementation.
    """

    interface.implements( interfaces.ITokenSource )
    
    def getSecrets(self):
        manager=queryUtility(IKeyManager)
        if manager is None:
            raise NoKeyManager
        return manager[u"_system"]

    def getSigningSecret(self):
        return self.getSecrets()[0]

    def signUserid(self, userid, secret=None):
        if secret is None:
            secret = self.getSigningSecret()

        return hmac.new(secret, userid, sha).digest()

    def createIdentifier(self, userid):
        signature=self.signUserid(userid)

        return "%s %s" % (signature, userid)

    def splitIdentifier(self, identifier):
        index=identifier.rfind(" ")
        if index==-1:
            raise ValueError

        return (identifier[:index], identifier[index+1:])

    def verifyIdentifier(self, identifier):
        try:
            secrets=self.getSecrets()
        except NoKeyManager:
            return False

        for secret in secrets:
            try:
                (signature, userid)=self.splitIdentifier(identifier)
                if  signature==self.signUserid(userid, secret):
                    # XXX if the secret is not the current signing secret we should reset the cookie
                    return True
            except (AttributeError, ValueError):
                continue

        return False

    def extractUserId(self, identifier):
        (signature, userid)=self.splitIdentifier(identifier)
        return userid




