"""

License GPL

"""

from zope.component import getUtility
from zope import interface

from zope.publisher.interfaces.http import IHTTPRequest
from zope.app.authentication.session import SessionCredentialsPlugin
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.app.security.interfaces import IAuthentication
from zope.app.container.contained import Contained

from persistent import Persistent

from ore.tokenauth import interfaces

import datetime
import binascii

class TokenCredentialsProvider(SessionCredentialsPlugin):
    
    cookie_name = "authtoken"
    cookie_lifetime = 0
    cookie_path = "/"
    
    def extractCredentials(self, request):
        if not IHTTPRequest.providedBy( request ):
            return None
        
        login = request.get(self.loginfield, None)
        password = request.get(self.passwordfield, None)
        cookie = request.get(self.cookie_name, None)

        # login attempt 
        if login and password:
            # verify the credentials and then setup token, needs a double login for
            # initial login attempts
            creds = {'login': login, 'password':password }
            # does assume a pluggable authentication utility
            for auth_name, auth in getUtility( IAuthentication ).getAuthenticatorPlugins():
                if auth.authenticateCredentials( creds ):
                    self.setupTokenSession( login, request )                    
                    break
            return creds

        # check for token
        if not self.cookie_name in request:
            return None

        # extract token
        try:
            return { 'token': binascii.a2b_base64(request.get(self.cookie_name)) }
        except binascii.Error:
            # If we have a cookie which is not properly base64 encoded it
            # can not be ours.
            return None

    def logout(self, request):
        if not IHTTPRequest.providedBy(request):
            return
        request.response.expireCookie(self.cookie_name, path=self.cookie_path )

    def setupTokenSession( self, login, request ):
        source = getUtility( interfaces.ITokenSource )        
        token = source.createIdentifier( login )
        cookie = binascii.b2a_base64( token ).rstrip()
        
        if isinstance( self.cookie_lifetime, int ) and self.cookie_lifetime:
            expires = ( datetime.datetime.now() +  datetime.timedelta( seconds=self.cookie_lifetime ) ).isoformat()
            request.response.setCookie( self.cookie_name, cookie, path=self.cookie_path, expires=expires )
        else:
            request.response.setCookie( self.cookie_name, cookie, path=self.cookie_path )
            
class TokenAuthenticationProvider( Persistent, Contained ):

    interface.implements( IAuthenticatorPlugin )

    prefix_set = ('',)
    
    def __init__( self, prefix_set=None):
        self.prefix_set = prefix_set or self.prefix_set
        
    def authenticateCredentials( self, credentials ):
        
        token = credentials.get('token')
        source = getUtility( interfaces.ITokenSource )
        if not token:
            return

        if not source.verifyIdentifier( token ):
            return 
            
        login = source.extractUserId( token )

        for name, plugin in getUtility( IAuthentication ).getAuthenticatorPlugins():
            for p in self.prefix_set:
                info = plugin.principalInfo( p + login )
                if info is None:
                    continue
                return info
            
    def principalInfo( self, id  ):
        return None
