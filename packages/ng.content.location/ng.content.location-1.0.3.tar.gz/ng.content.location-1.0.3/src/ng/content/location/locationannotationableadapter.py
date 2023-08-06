### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: locationannotationableadapter.py 52798 2009-04-02 14:25:14Z corbeau $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52798 $"

from locationannotation import LocationAnnotation
from zope.annotation.interfaces import IAnnotations 
from zope.schema import getFieldNames

from interfaces import locationannotationkey

def ILocationAnnotationAbleAdapter(context) :

    try :
        an = IAnnotations(context)[locationannotationkey]
    except KeyError :
        an = IAnnotations(context)[locationannotationkey] = LocationAnnotation()
        an.__parent__ = context
    return an
