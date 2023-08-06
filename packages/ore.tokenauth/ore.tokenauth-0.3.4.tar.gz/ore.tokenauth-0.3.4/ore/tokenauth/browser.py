# not used currently, no ui

#from zope.app.pagetemplatefile import ViewPageTemplateFile

class TokenSessionManagement( object ):

    #template = ViewPageTemplateFile('manage.pt')
    
    def __init__( self, context, request ):
        self.context = context
        self.request = request

    def __call__( self ):
        return "hello world"
        self.update()
        return self.template()

    def update( self ):
        pass
    
