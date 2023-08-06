"""
$Id: base.py 1965 2007-05-22 03:41:22Z hazmat $
"""

from zope.app.annotation.interfaces import IAnnotations
from zope.interface import implements
from persistent.dict import PersistentDict

try:
    from Products.Five.formlib.formbase import FormBase, SubPageForm
except ImportError:
    from zope.formlib.form import FormBase, SubPageForm

from zope.formlib import form

from interfaces import IViewComponent

class BaseEventManager( object ):
    """ a mixin for viewlet manager which for a private event channel
    """
    def notify( self, event ):
        """ available during update and render phases
        """
        for viewlet in self.viewlets:
            viewlet.notify( event )

class BaseStorageManager( object ):
    """ a mixin for a viewlet manager to provide a persistent annotation storage
        for use by templates.
    """
    _storage = None

    annotation_key = "ore.asset.viewlet"

    def storage( self, name=None ):
        """ name if given is the key of a persistent dictionary off of
        the annotation.
        """ 
        if self._storage is None:
            annotations = IAnnotations( self.context )
            self._storage = annotations.get( self.annotation_key, None )
            if self._storage is None:
                annotations[ self.annotation_key ] = self._storage = PersistentDict()

        if name is None:
            return self._storage
        if name in self._storage:
            return self._storage[name]
        
        self._storage[ name ] = PersistentDict()
        return self._storage[name]
        
            
class BaseEventViewlet( object ):

    accepts = ()
    
    def notify( self, event ):
        """ receive an event
        """

class BaseFormViewlet( SubPageForm ):
    """ a mixin for viewlet which utilize formlib
    """
    form_template = FormBase.template    
    renderForm = FormBase.render    
    form_fields = form.Fields()
    
class BaseMultiPage( object ):

    template_mapping = {}
    page_sequence = []

    current_page = None # set during update

    def renderNext( self ):
        page_name = self.nextPage()
        return self.renderMultiPage( page_name )
    
    def renderMultiPage( self, page_name ):
        template = self.template_mapping[ page_name ]
        template = template.__of__( self.context ) 
        return template()

    def nextPage( self ):
        """ find next page name, return none if no new page.
        """
        if not self.current_page:
            self.current_page = self.page_sequence[0]
            idx = 0
        else:
            idx = self.page_sequence.index( self.current_page ) + 1
        if len( self.page_sequence ) <= idx:
            # wrap around on completion
            return self.page_sequence[0]
        return self.page_sequence[ idx ]

class ViewComponent( BaseEventViewlet, BaseFormViewlet ):

    implements( IViewComponent )

    component_key = None
    active = True
    #template = None
    
    #def render(self):
    #    return self.template()

    def update( self ):
        if self.component_key and not self.request.has_key( self.component_key ):
            self.active = False
            return 
        super(ViewComponent, self).update()

class ViewletTraverser( object ):
    """ a traversal adapter for the view
    """

class PersistentViewComponent( ViewComponent, BaseStorageManager ):
    pass

