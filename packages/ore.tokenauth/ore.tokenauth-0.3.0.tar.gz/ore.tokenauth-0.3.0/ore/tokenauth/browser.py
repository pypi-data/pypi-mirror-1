
from zope.app.pagetemplatefile import ViewPageTemplateFile


class TokenSessionManagement( object ):

    template = ViewPageTemplateFile('manage.pt')
    
    def __init__( self, context, request ):
        self.context = context
        self.request = request

    def __call__( self ):
        self.update()
        return self.template()
