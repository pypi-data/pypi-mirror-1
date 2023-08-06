### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: tagrubricannotationableadapter.py 51876 2008-10-20 18:01:50Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51876 $"

from tagrubricannotation import TagRubricAnnotation
from zope.annotation.interfaces import IAnnotations 
from zope.schema import getFieldNames

from interfaces import tagrubricannotationkey

def ITagRubricAnnotationAbleAdapter(context) :

    try :
        an = IAnnotations(context)[tagrubricannotationkey]
    except KeyError :
        an = IAnnotations(context)[tagrubricannotationkey] = TagRubricAnnotation()
        an.__parent__ = context
    return an
