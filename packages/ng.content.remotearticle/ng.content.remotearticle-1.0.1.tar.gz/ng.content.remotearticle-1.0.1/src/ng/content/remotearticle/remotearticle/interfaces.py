### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.content.remote.remotearticle package

$Id: interfaces.py 49416 2008-01-13 08:31:17Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49416 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Bool, Datetime
from zope.app.container.interfaces import IContained, IContainer
from ng.content.article.interfaces import ISContent, IDocShortLogo
from ng.content.article.article.interfaces import IArticle, IArticleContainerOrdered
from ng.app.remotefs.interfaces import IRemoteObject, IRemoteObjectAdd, IRemoteStat
from ng.app.remotefs.remotefile.interfaces import IRemoteFile

class IRemoteBody(ISContent,IRemoteFile) :
    """ IRemoteBody interface """

class IRemoteArticleShort(IDocShortLogo,IRemoteObjectAdd) :
    """ IRemoteArticleShort interface """

class IRemoteArticle(IRemoteArticleShort,IRemoteObject, IRemoteBody,IRemoteStat) :
    """ IRemoteArticle interface """


