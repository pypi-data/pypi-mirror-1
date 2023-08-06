### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: tagitemannotation.py 51876 2008-10-20 18:01:50Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51876 $"

from persistent import Persistent
from zope.interface import Interface
from zope.interface import implements,implementedBy
from interfaces import ITagItemAnnotation,ITagItemAnnotationAble,tagitemannotationkey
from zope.location.interfaces import ILocation

class TagItemAnnotation(Persistent) :
    __doc__ = ITagItemAnnotation.__doc__
    implements(ITagItemAnnotation,ILocation)
    __parent__=None
    __name__= "++annotations++" + tagitemannotationkey


    tags = set([])
    def __init__(self) :
        self.tags = set([])    