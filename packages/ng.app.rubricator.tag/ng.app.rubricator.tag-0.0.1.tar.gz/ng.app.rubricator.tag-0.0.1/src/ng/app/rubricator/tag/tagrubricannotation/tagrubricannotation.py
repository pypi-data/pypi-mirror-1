### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: tagrubricannotation.py 51587 2008-08-31 18:00:21Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51587 $"

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

    # See tagrubricannotation.interfaces.ITagRubricAnnotation
    suffixes = ''
    keyword = []
    area = []
    gender = []
    wikiword=''    