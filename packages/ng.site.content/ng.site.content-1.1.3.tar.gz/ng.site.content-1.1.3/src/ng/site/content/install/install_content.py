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

def installAbout(context, **kw):
    """ Создаёт раздел about
    """
    about = context[u'about'] = Division()

    about.title = kw['about']
    about.abstract = kw['about_abstract']
    about.author = kw['author']
    IObjectQueueAnnotation(about).use = False
    
    return "Success"

def installDictionary(context, **kw):
    """ Create Dictionary Division """
    dictionary = context[u'dictionary'] = Division()

    dictionary.title = kw['dictionary']
    dictionary.author = kw['author']
    IObjectQueueAnnotation(dictionary).use = True
    IObjectQueueAnnotation(dictionary).islast = True
    
def installArticles(context, **kw):
    """ Создаёт раздел Articles
    """

    article = context[u'article'] = Division()

    article.title = kw['article']
    article.abstract = kw['article_abstract']
    article.author = kw['author']
    IObjectQueueAnnotation(article).use = False

    sm = context.getSiteManager()
    sm.registerUtility(context[u'article'], provided=IContainer, name=u'article')

    return "Success"

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

def installNews(context, **kw):
    """ Создаёт раздел News
    """
    news = context[u'news'] = Division()

    news.title = kw['news']
    news.abstract = kw['news_abstract']
    news.author = kw['author']

    sm = context.getSiteManager()
    sm.registerUtility(context[u'news'], provided=IContainer, name=u'news')
    IObjectQueueAnnotation(news).use = True
    IObjectQueueAnnotation(news).islast = False

    return "Success"

def installRubrics(context, **kw) :
    rubrics = kw['rubrics']
    
    for rubric in rubrics :
       division = Division()
       division.title = rubric.title
       division.abstract = rubric.abstract
       division.author = kw['author']
       context[rubric.name] = division
       IObjectQueueAnnotation(division).use = True
       IObjectQueueAnnotation(division).islast = False

    return "Success"
