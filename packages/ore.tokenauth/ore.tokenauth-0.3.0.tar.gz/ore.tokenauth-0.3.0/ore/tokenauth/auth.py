"""

License GPL

"""

from zope.publisher.interfaces.http import IHTTPRequest
from zope.app.authentication.session import SessionCredentialsPlugin
from zope.app.authentication.interfaces import IAuthentication
from zope.component import getUtility

from ore.authtoken import interfaces

import datetime
import binascii

class TokenCredentialsProvider(SessionCredentialsPlugin):
    
    cookie_name = "mobilize.authtoken"
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
            for auth in getUtility( IAuthentication ).getAuthenticatorPlugins():
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
        source = getUtility( interfaces.IAuthTokenSource )        
        token = source.createIdentifier( login )
        cookie = binascii.b2a_base64( token ).rstrip()
        
        if isinstance( self.cookie_lifetime, int ) and self.cookie_lifetime:
            expires = ( datetime.datetime.now() +  datetime.timedelta( seconds= self.cookie_lifetime ) ).isoformat()
            request.response.setCookie( self.cookie_name, cookie, path=self.path, expires=expires )
        else:
            request.response.setCookie( self.cookie_name, cookie, path=self.path )
            
class TokenAuthenticationProvider( object ):

    @property
    def token_source( self ):
        return getUtility( interfaces.ITokenSource )
    
    def authenticateCredentials( self, credentials ):
        token = credentials.get('token')

        if not token:
            return
        if not self.token_source.verifyToken( token ):
            return 
            
        login = self.token_source.extractLogin( token )
        
        for plugin in getUtility( IAuthentication ).getAuthenticatorPlugins():
            info = plugin.principalInfo( login )
            if info is None:
                continue
            return info
            
    def principalInfo( self, id  ):
        return None
