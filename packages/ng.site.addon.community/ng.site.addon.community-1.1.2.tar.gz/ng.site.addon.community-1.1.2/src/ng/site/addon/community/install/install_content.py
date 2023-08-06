### -*- coding: utf-8 -*- #############################################
#######################################################################
"""installAbout, installArticles, installMirrors, installNews, installRubric
and installRubrics scripts for the Zope 3 based ng.site.content.install package

$Id: install_content.py 52501 2009-02-10 21:43:24Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 52501 $"

from zope.app.folder.folder import Folder

from zope.app.component.hooks import setSite
from zope.app.component import site

from ng.content.article.division.division import Division
from ng.content.article.article.article import Article
from ng.app.objectqueue.interfaces import IObjectQueueAnnotation
from zope.app.container.interfaces import IContainer

def installCommunity(context, **kw):
    """ Создаёт раздел Community
    """

    community = context[u'community'] = Division()

    community.title = kw['community']
    community.author = kw['author']
    IObjectQueueAnnotation(community).use = False

    sm = context.getSiteManager()
    sm.registerUtility(context[u'community'], provided=IContainer, name=u'community')

    return "Success"

