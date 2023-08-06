"""
a viewlet management interface into a container
"""


from zope.app.container.interfaces import IContainer, IOrderedContainer
from zope import component
from zope.formlib import form

from zc.table import table

from base import BaseFormViewlet
from core import ComponentViewlet

from Products.Five.viewlet.viewlet import ViewletBase

class ContainerViewlet( ComponentViewlet, BaseFormViewlet ):

    form_fields = form.Fields()
    prefix = "clist"

    columns = None
    selection_column = None

    formatter_factory = table.StandaloneFullFormatter
    
    def getContainerContext(self):
        return self.context

    #################################
    def render( self ):
        return self.template( container=self.container )

    def show( self ):
        return True

    def update( self ):
        context = self.getContainerContext() 
        self._is_ordered = IOrderedContainer.providedBy( context ) and True or False
        self.container = context
        # update for component and form
        super( ContainerViewlet, self ).update()
        BaseFormViewlet.update( self )
        
    #################################
         
    def listing( self ):
        columns = self.columns

        formatter = self.formatter_factory( self.container,
                                            self.request,
                                            self.container.values(),
                                            prefix="form",
                                            visible_column_names = [c.name for c in columns],
                                            #sort_on = ( ('name', False)
                                            columns = columns )
        formatter.cssClasses['table'] = 'listing'
        return formatter()

    def isNotEmpty( self, *args):
        return bool( len( self.container ) )

    def isOrdered( self, *args ):
        return self._is_ordered
    
    def move_nodes( self, action, data, delta=-1 ):
        # delta constraint, increments are one
        selected = self._getNodes( action, data )

        keys = self.container.keys()
        if not selected or not keys or len(keys)==1:
            return
        
        min, max = 0, len(keys)
        
        for k in selected:
            pos = keys.index( k.item_id  )
            if pos == min and delta == -1:
                continue
            if pos == (max-1) and delta == 1:
                continue
            pk = keys[ pos+delta ]
            keys[ pos ] = pk
            keys[ pos+delta ] = k.item_id
        self.container.updateOrder( list(keys) )
    
    @form.action("Delete", condition="isNotEmpty")
    def handle_remove_node( self, action, data ):
        selected = self._getNodes( action, data )
        for s in selected:
            del self.container[ s.__name__ ]

    @form.action("Up", condition="isOrdered")
    def handle_move_node_up( self, action, data ):
        self.move_nodes( action, data, delta=-1 )
        
    @form.action('Down', condition="isOrdered")
    def handle_move_node_down( self, action, data ):
        self.move_nodes( action, data, delta=1 )        
        
    def _getNodes( self, action, data ):
        selected = self.selection_column.getSelected( self.container.values(), self.request)
        self.form_reset = True
        return selected
    
