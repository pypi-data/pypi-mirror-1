### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Annotation-Container to contain comment

$Id: commentannotation.py 51580 2008-08-31 13:52:31Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51580 $"

from persistent import Persistent
from zope.interface import Interface
from zope.interface import implements,implementedBy
from interfaces import ICommentAnnotation,ICommentAnnotationAble,\
    ICommentContainerOrdered, ICommentContained, commentannotationkey

from zope.location.interfaces import ILocation
from zope.app.container.ordered import OrderedContainer



class CommentAnnotation(OrderedContainer) :
    __doc__ = ICommentAnnotation.__doc__
    implements(ICommentAnnotation,ICommentContainerOrdered,ILocation)
    __parent__ = None
    __name__ = "++annotations++" + commentannotationkey

    isallow = True

    def __init__(self,context) :
        self.__parent__ = context
        super(CommentAnnotation,self).__init__()
