### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: tagrubricsearchadapter.py 51587 2008-08-31 18:00:21Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51265 $"

from zope.interface import implements
from zope.component import adapts
from interfaces import ITagRubricSearch, ITagRubricAnnotation, ITagRubricAnnotationAble

class TagRubricSearchAdapter(object) :
     """Interface for index objects"""
     
     implements(ITagRubricSearch)
     adapts(ITagRubricAnnotationAble)
    
     def __init__(self,context,*kv,**kw) :
         self.context = ITagRubricAnnotation(context)

     @property
     def tags(self) :
         return set(tuple(self.context.tags) + tuple(self.context.tags_added[:]))
