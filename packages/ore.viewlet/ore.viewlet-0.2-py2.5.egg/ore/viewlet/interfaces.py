"""
$Id: interfaces.py 1962 2007-05-18 19:37:09Z hazmat $
"""

from zope.interface import Interface
from zope.viewlet import interfaces as viewapi
from zope.formlib.interfaces import IForm

class IEventManager( Interface ):
    """ an object implementing a private event channel
    """
    
    def notify( event ):
        """
        publish an event to contained viewlets
        """

class IEventViewlet( Interface ):

    def notify( event ):
        """
        receive an event on the private event channel 
        """

class IStorageManager( Interface ):
    """ an providing persistent annotation access for values
    """
    
    def storage( name=None ):
        """ return viewlet persistent mapping, if name specified its
        the mapping is namespaced
        """

class IFormViewlet( viewapi.IViewlet, IForm ):
    """ a viewlet which utilizes formlib for forms or actions
    """

class IViewComponent( viewapi.IViewlet ):
    """ a functional component viewlet with ajax interaction with the
    browser, component assets are directly addressable by url, they are
    not view themselves.
    """

    def show( ):
        """ should this view component be displayed on the current page
        """

