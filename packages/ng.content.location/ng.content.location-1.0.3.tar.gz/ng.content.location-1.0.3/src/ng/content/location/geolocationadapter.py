### -*- coding: utf-8 -*- #############################################
#######################################################################
""" ILocationAnnotationAble to IGeolocation adapter for the Zope 3 based ng.content.location package

$Id: geolocationadapter.py 52833 2009-04-06 10:01:29Z corbeau $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52833 $"

from interfaces import ILocationAnnotation
from zope.security.proxy import removeSecurityProxy

class GeolocationAdapter(object) :
    def __init__(self, context) :
        self.location = (
            removeSecurityProxy(ILocationAnnotation(context).latitude),
            removeSecurityProxy(ILocationAnnotation(context).logtitude),
        )
