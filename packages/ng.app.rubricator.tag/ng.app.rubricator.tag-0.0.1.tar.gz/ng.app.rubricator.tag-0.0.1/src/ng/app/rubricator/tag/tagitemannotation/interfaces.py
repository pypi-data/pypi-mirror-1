### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 51587 2008-08-31 18:00:21Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51587 $"
 
from zope.interface import Interface

from zope.schema import TextLine, Set, Choice
from zope.app.container.interfaces import IContained, IContainer
from ng.app.rubricator.tag.tagvocabulary.tagvocabulary import TagVocabulary


class ITagItemAnnotationAble(Interface) :
    pass

class ITagItemAnnotation(Interface) :
    """ """
    tags = Set(title=u'Keywords',
                  value_type = Choice(source = TagVocabulary()),
                  required=False,
                  )

tagitemannotationkey="ng.app.rubricator.tag.tagitemannotation.TagItemAnnotation"

