### -*- coding: utf-8 -*- #############################################
#######################################################################
"""installAbout, installArticles, installMirrors, installNews, installRubric
and installRubrics scripts for the Zope 3 based ng.site.content.install package

$Id: product.py 49265 2008-01-08 12:18:26Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49265 $"

from zope.app.folder.folder import Folder

from zope.app.component.hooks import setSite
from zope.app.component import site

from ng.content.article.division.division import Division
from ng.content.article.article.article import Article
from ng.app.objectqueue.interfaces import IObjectQueueAnnotation
from zope.app.container.interfaces import IContainer

def installMirrors(context, **kw):
    """ Создаёт раздел Mirrors
    """
    mirror = context[u'mirror'] = Division()

    mirror.title = kw['mirror']
    mirror.abstract = kw['mirror_abstract']
    mirror.author = kw['author']
    IObjectQueueAnnotation(mirror).use = True
    IObjectQueueAnnotation(mirror).islast = True

    return "Success"

