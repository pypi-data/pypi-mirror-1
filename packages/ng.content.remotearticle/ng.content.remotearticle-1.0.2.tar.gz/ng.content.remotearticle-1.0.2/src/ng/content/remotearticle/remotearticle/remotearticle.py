### -*- coding: utf-8 -*- #############################################
#######################################################################
"""RemoteArticle class for the Zope 3 based ng.content.article package

$Id: remotearticle.py 52024 2008-11-14 09:59:13Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 52024 $"
__date__    = "$Date: 2008-11-14 12:59:13 +0300 (Птн, 14 Ноя 2008) $"
 
from zope.interface import implements
from ng.content.article.article.interfaces import IArticle,IArticleContainerOrdered

from ng.content.article.article.article import ArticleBase
from ng.app.remotefs.remotefile.remotefile import RemoteFile
from ng.app.remotefs.interfaces import IRemoteObject
from interfaces import IRemoteArticle

class RemoteArticle(ArticleBase, RemoteFile):
    __doc__ = "RemoteArticle class"

    implements(IRemoteArticle, IArticle,  IArticleContainerOrdered)
