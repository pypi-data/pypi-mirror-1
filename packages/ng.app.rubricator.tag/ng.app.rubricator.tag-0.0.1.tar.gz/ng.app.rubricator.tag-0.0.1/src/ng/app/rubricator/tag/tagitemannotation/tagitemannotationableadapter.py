### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: tagitemannotationableadapter.py 51587 2008-08-31 18:00:21Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51587 $"

from tagitemannotation import TagItemAnnotation
from zope.annotation.interfaces import IAnnotations 
from zope.schema import getFieldNames

from interfaces import tagitemannotationkey

def ITagItemAnnotationAbleAdapter(context) :

    try :
        an = IAnnotations(context)[tagitemannotationkey]
    except KeyError :
        an = IAnnotations(context)[tagitemannotationkey] = TagItemAnnotation()
        an.__parent__ = context
    return an
