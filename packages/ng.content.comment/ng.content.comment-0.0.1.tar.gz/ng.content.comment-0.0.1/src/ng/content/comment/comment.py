### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Comment class for the Zope 3 based comment annotation package

$Id: comment.py 51580 2008-08-31 13:52:31Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51580 $"

from zope.interface import implements
from persistent import Persistent
from zope.app.container.contained import Contained
from interfaces import IComment,ICommentContained
import datetime
import pytz

class Comment(Contained,Persistent) :
    implements(IComment,ICommentContained)

    def __init__(self,*kv,**kw) :
        super(Comment,self).__init__(*kv,**kw)
        self.created = datetime.datetime.now(pytz.utc)        

    title = u""
    abstract = u""
    created = datetime.datetime.now(pytz.utc)
    author = u""



