### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.content.location package

$Id: interfaces.py 52880 2009-04-07 19:42:08Z cray $
"""
__author__  = "Yegor Shershnev, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52880 $"
 
from zope.interface import Interface

from zope.schema import Int, Float
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint


class ILocationAnnotationAble(Interface) :
    pass

class ILocationAnnotation(Interface) :
    """ Annotation that contains parameters for make request to create
        static map from maps.google.com
    """

    latitude = Float(
        title = u"Latitude",
        description = u"Latitude of object",
        required = True)
    
    longtitude = Float(
        title = u"Longtitude",
        description = u"Longtitude of object",
        required = True)

    zoom = Int(
        title = u"Zoom",
        description = u"Zoom of map",
        required = False)

locationannotationkey="locationannotation.locationannotation.LocationAnnotation"
