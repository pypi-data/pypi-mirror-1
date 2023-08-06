### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The cachestore interface

Interfaces for the Zope 3 based cachestore package

$Id: interfaces.py 49774 2008-01-03 13:50:48Z cray $
"""
__author__  = "Anatoly Bubenkov, 2006"
__license__ = "GPL"
__version__ = "$Revision: 49774 $"

from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Choice
from zope.schema import Int
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.component.interfaces import ILocalSiteManager
from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.intid.interfaces import IIntIds
from zope.app.component.vocabulary import UtilityNames
from ng.app.converter.object2psadapter.interfaces import IPropertySheet

class ICachestore(Interface):
    """Cache store interface"""
    
    intIdsName = Choice(title = u'Name of IntIds utility',
                          description = u'Name of IntIds utility',
                          default = None,
                          required = True,
                          vocabulary = 'IntIdsNames'
                          )
        
    max_caching_time = Int(title = u'Max caching time, seconds',
                          description = u'Max caching time, seconds',
                          default = 3600*24*10,
                          required = True)

    eventdelta = Int(title = u'Event delta time',
                          description = u'Delta time beetween call event handler and'
                                'date of modifcation object ',
                          default = 2,
                          required = True)

        
    def regenerate_all():
        """Regenerate Cache"""
    
    def regenerate(ob):
        """renegerate object on cache"""
	
    def clean():
        """Clean Cache"""
    
class ICachestoreStat(Interface):
    """ A cachestore statistic interface """
    pass
        
class ICachestoreContent(Interface) :
    """ Interface to mark cachestore content """

class ICachestoreContained(IContained):
    """Interface that specifies the type of objects that can contain CacheStore."""
    __parent__ = Field(
        constraint = ContainerTypesConstraint(ILocalSiteManager, ICachestore))
    
class ICachestoreContainer(IContainer) :
    def __setitem__(name, object) : 
        """ Add IArticle Content """

    __setitem__.precondition = ItemTypePrecondition(ICachestoreContent)

