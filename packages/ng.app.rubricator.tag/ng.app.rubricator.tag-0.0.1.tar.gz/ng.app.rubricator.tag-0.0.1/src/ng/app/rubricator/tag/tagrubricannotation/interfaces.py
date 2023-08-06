### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 51587 2008-08-31 18:00:21Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51587 $"
 
from zope.interface import Interface

from zope.schema import TextLine, Set, Tuple, Choice
from zope.app.container.interfaces import IContained, IContainer
from ng.app.rubricator.tag.tagvocabulary.tagvocabulary import TagVocabulary

class ITagRubricAnnotationAble(Interface) :
    pass

class ITagRubricAnnotation(Interface) :
    """ """

    tags = Set(title=u'Keywords',
                  value_type = Choice(source = TagVocabulary()),
                  required=False,
                  )

    tags_added = Tuple(title=u'New keywords',
                    description=u'Some keywords',
                    required=False,
                    default=(),
                    value_type=TextLine(title=u'keyword'),
                   )

class ITagRubricSearch(Interface) :
    tags = Set(title=u'Keywords',
                  value_type = Choice(source = TagVocabulary()),
                  required=False,
                  )
                
tagrubricannotationkey="ng.app.rubricator.tag.tagrubricannotation.TagRubricAnnotation"

