### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: tagrubricannotation.py 51876 2008-10-20 18:01:50Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51876 $"

from persistent import Persistent
from zope.interface import Interface
from zope.interface import implements,implementedBy
from interfaces import ITagRubricAnnotation,ITagRubricAnnotationAble,tagrubricannotationkey

from zope.location.interfaces import ILocation
class TagRubricAnnotation(Persistent) :
    __doc__ = ITagRubricAnnotation.__doc__
    implements(ITagRubricAnnotation,ILocation)
    __parent__=None
    __name__= "++annotations++" + tagrubricannotationkey

    def __init__(self,*kv,**kw) :
        super(TagRubricAnnotation,self).__init__(*kv,**kw)
        self.tags = set([])
        self.tags_added = ()

    tags = set([])
    tags_added = ()
    