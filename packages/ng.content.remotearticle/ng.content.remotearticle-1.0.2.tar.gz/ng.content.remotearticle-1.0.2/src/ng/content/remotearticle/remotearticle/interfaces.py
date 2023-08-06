### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.content.remote.remotearticle package

$Id: interfaces.py 52024 2008-11-14 09:59:13Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 52024 $"
 
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


