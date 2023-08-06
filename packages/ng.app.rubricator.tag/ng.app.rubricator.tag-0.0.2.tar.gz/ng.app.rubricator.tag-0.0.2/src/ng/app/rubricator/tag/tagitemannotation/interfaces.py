### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 51876 2008-10-20 18:01:50Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51876 $"
 
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

