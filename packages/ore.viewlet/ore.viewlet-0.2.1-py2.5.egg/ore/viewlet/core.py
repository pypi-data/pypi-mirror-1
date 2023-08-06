"""
$Id: core.py 1965 2007-05-22 03:41:22Z hazmat $
"""

from zope.viewlet.viewlet import ViewletBase
import base

class EventViewlet( ViewletBase, base.BaseEventViewlet ):
    pass

class FormViewlet( ViewletBase, base.BaseFormViewlet ):

    def update( self ):
        super( FormViewlet, self).update()        
        super( base.BaseFormViewlet, self ).update()

class ComponentViewlet( ViewletBase, base.ViewComponent ):

    def update( self ):
        super( ComponentViewlet, self ).update()
        super( base.ViewComponent, self ).update()

