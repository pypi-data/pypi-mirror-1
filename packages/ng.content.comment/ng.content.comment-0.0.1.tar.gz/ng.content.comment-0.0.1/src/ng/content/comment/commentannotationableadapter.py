### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: commentannotationableadapter.py 51580 2008-08-31 13:52:31Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51580 $"

from commentannotation import CommentAnnotation
from zope.annotation.interfaces import IAnnotations 
from zope.schema import getFieldNames

from interfaces import commentannotationkey

def ICommentAnnotationAbleAdapter(context) :

    try :
        an = IAnnotations(context)[commentannotationkey]
    except KeyError :
        an = IAnnotations(context)[commentannotationkey] = CommentAnnotation(context)
    return an
