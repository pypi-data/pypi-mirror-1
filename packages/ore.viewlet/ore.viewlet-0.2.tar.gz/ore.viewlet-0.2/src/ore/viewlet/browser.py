
try:
    from Products.Five.browser import BrowserView
except:
    from zope.publisher.browser import BrowserView

class ViewletView( BrowserView ):


    def __call__( self ):
        pass


class ViewletViewTraverser( ):
    pass
