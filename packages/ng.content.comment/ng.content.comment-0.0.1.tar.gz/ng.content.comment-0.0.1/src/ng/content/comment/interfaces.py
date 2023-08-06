### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 51580 2008-08-31 13:52:31Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51580 $"
 
from zope.interface import Interface

from zope.schema import TextLine, Choice, Tuple, Field, Text, Datetime, Bool
from zope.app.container.interfaces import IContained, IContainer, IOrderedContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from zope.schema import Choice
from zope.schema.vocabulary import SimpleVocabulary
from ng.content.article.interfaces import ICommonContainer, IDocTitle,IDocAbstract


def forbidden(container) :
  return ContainerTypesConstraint(ICommonContainer)(container) and ICommentAnnotation(container).isallow
                


class ICommentAnnotationAble(Interface) :
    pass

class ICommentAnnotation(Interface) :
    """ """
    isallow = Bool(title=u"Comments is allowed", default=True)

class IComment(IDocAbstract) :
    """ Commentary interface """

commentannotationkey="commentannotation.commentannotation.CommentAnnotation"

class ICommentContent(Interface) :
    """ Interface for comment content """

class ICommentContained(IContained,ICommentContent) :
    """ Comment Contained """
    __parent__ = Field(constraint = forbidden)

class ICommentContainer(IOrderedContainer,ICommonContainer) :
    """ Comment Container """
    
    def __setitem__(name, object) : 
        """ Add IComment Content """

    __setitem__.precondition = ItemTypePrecondition(ICommentContent)                    

class ICommentContainerOrdered(ICommentContainer) :
    """ Comment Container """


    
