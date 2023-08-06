### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Vocabulary for tagrubricannotation used to get values from
IIndexValues 'tags' utility

$Id: tagvocabulary.py 51587 2008-08-31 18:00:21Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51265 $"

from zope.app.zapi import getUtility
from zope.interface import implements
from zope.schema.interfaces import  IContextSourceBinder
from zc.catalog.interfaces import IIndexValues
from zope.interface import implements, alsoProvides
from zope.schema.vocabulary import SimpleVocabulary

class TagVocabulary(object) :
    implements(IContextSourceBinder)

    def __init__(self,name='tags') :
        self.name = name
        
    def __call__(self,context) :
        vocabulary = SimpleVocabulary.fromValues(
          sorted(
            getUtility(IIndexValues,context=context,name=self.name).values()
            )
          )
        return vocabulary

