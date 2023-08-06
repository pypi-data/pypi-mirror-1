### -*- coding: utf-8 -*- #############################################
#######################################################################
"""LocationAnnotationView class for ng.content.location product

$Id: viewlocationannotation.py 52880 2009-04-07 19:42:08Z cray $
"""
__author__  = "Yegor Shershnev, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52880 $"
 
from ng.content.location.interfaces import ILocationAnnotation
from ng.app.registry.interfaces import IRegistry

class LocationAnnotationView(object) :

    def __init__(self,*kv,**kw) :
        super(LocationAnnotationView,self).__init__(*kv,**kw)
        self.parent = self.context
        registry =  IRegistry(self.context)
        self.context = context = ILocationAnnotation(self.context)
        registry =  IRegistry(self.context)
        if context.zoom is None :
            self.zoom = registry.param("googlemapzoom",10)
        else :
            self.zoom = context.zoom            

        self.size = registry.param("googlemapsize","512x512")

        self.key = registry.param("googlemapkey","")

        d = {
          'latitude' : context.latitude,
          'longtitude': context.longtitude,
          'zoom' : self.zoom,
          'size' : self.size,
          'key'  : self.key  
        }
        self.param = "center=%(latitude)s,%(longtitude)s&zoom=%(zoom)s&size=%(size)s&markers=%(latitude)s,%(longtitude)s,bluea&key=%(key)s" % d
        self.url = "http://maps.google.com/staticmap?" + self.param
        self.googlemapurl = "http://maps.google.com/?ll=%(latitude)s,%(longtitude)s&z=%(zoom)s" % d