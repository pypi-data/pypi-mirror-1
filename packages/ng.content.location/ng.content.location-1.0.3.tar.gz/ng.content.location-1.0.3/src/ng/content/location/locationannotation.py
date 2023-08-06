### -*- coding: utf-8 -*- #############################################
#######################################################################
"""LocationAnnotation class for the Zope 3 based ng.content.location package

$Id: locationannotation.py 52880 2009-04-07 19:42:08Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52880 $"

from persistent import Persistent
from zope.interface import Interface
from zope.interface import implements, implementedBy
from interfaces import ILocationAnnotation, ILocationAnnotationAble, locationannotationkey
from zope.location.interfaces import ILocation

class LocationAnnotation(Persistent) :
    
    __doc__ = ILocationAnnotation.__doc__
    
    implements(ILocationAnnotation, ILocation)
    
    __parent__ = None
    
    __name__ = "++annotations++" + locationannotationkey
    
    latitude = 0.0
    
    longtitude = 0.0
    
    zoom = 10
