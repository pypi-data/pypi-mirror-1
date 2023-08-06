### -*- coding: utf-8 -*- #############################################
#######################################################################
"""installConverter and installMapper scripts for the Zope 3 based
ng.site.content.install package

$Id: product.py 49265 2008-01-08 12:18:26Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49265 $"


from zope.app.folder.folder import Folder

from zope.app.component.hooks import setSite
from zope.app.component import site
from zope.app.component.site import SiteManagementFolder

from ng.app.converter.converter.converterhead.converterhead import ConverterHead
from ng.app.converter.converter.converterrest.converterrest import ConverterReST
from ng.app.converter.converter.converterregexp.converterregexp import ConverterRegexp
from ng.app.converter.converter.converterst.converterst import ConverterST
from ng.app.converter.converter.converterchain.converterchain import ConverterChain
from ng.app.converter.converter.convertercontainer.convertercontainer import ConverterContainer
from ng.app.converter.converter.converterxslt.converterxslt import ConverterXSLT
from ng.app.converter.converter.converterselect.converterselect import ConverterSelect

from ng.app.converter.converter.converterhead.interfaces import IConverterHead
from ng.app.converter.converter.converterrest.interfaces import IConverterReST
from ng.app.converter.converter.converterregexp.interfaces  import IConverterRegexp
from ng.app.converter.converter.converterst.interfaces import IConverterST
from ng.app.converter.converter.converterchain.interfaces import IConverterChain
from ng.app.converter.converter.convertercontainer.interfaces import IConverterContainer
from ng.app.converter.converter.converterxslt.interfaces import IConverterXSLT
from ng.app.converter.converter.converterselect.interfaces import IConverterSelect
from ng.app.converter.converter.converterannotator.interfaces import IConverterAnnotator

from ng.app.converter.cachestore.cachestore import Cachestore

from ng.app.converter.converter.converterchain.converterchain import ConverterChain
from ng.app.converter.converter.converterannotator.converterannotator import ConverterAnnotator
from ng.app.converter.converter.interfaces import IConverter
from ng.app.converter.cachestore.interfaces import ICachestore

from ng.app.converter.mapper.mapperobject.mapperobject import MapperObject
from ng.app.converter.mapper.mapperobject.interfaces import IMapperObject
from ng.app.converter.mapper.mapperinterface.mapperinterface import MapperInterface
from ng.app.converter.mapper.mapperattribute.mapperattribute import MapperAttribute
from ng.app.converter.mapper.mapperattributeitem.mapperattributeitem import MapperAttributeItem


def installConverter(context, **kw):
    """ Install all converters """
    sm = context.getSiteManager()
    converter = sm[u'converter'] = SiteManagementFolder()
    base = converter[u'base'] = SiteManagementFolder()
    
    for name,regexp,format in (
        ('absolute_url','(?<==")(?P<url>%40%40searchpage)','http://dreambot.ru/%(url)s'),
        ('comment-killer','(?m)^\s*(###|\*\*\*|#(TODO|FIXME|Q|A))\s*.*$',' '),
        ('degenerator','<meta name="generator" content="Docutils 0.4: http://docutils.sourceforge.net/" />',' '),
        ('keyword-killer','\[keyword:(?P<word>[^\]]+):(?P<word2>[^\]]+)\]','%(word2)s'),
        ('keyword-killer-simple','\[keyword:(?P<word>[^:\]]+)\]','%(word)s'),
        ('keyword-reference','\[keyword:(?P<word>[^\]]+):(?P<word2>[^\]]+)\]','<a title="Словарь: %(word)s" href="%%40%%40searchpage.html?keyword.any_of:record:tuple=%(quote(word))s">%(word2)s</a>'),
        ('keyword-reference-simple','\[keyword:(?P<word>[^:\]]+)\]','<a title="Словарь: %(word)s" href="%%40%%40searchpage.html?keyword.any_of:record:tuple=%(quote(word))s">%(word)s</a>'),
        ('killdivabstractstyle','\s+div.abstract\s+{\s+margin:\s+2em\s+5em\s+}',' '),
        ('killrestchaptersign','(?P<char>.)(?P=char){10,}',' '),
        ('name-killer','\[name:(?P<word>[^\]]+):(?P<title>[^\]]+)\]','%(title)s'),
        ('name-killer-simple','\[name:(?P<word>[^\]]+)\]','%(word)s'),
        ('name-reference','\[name:(?P<word>[^\]]+):(?P<title>[^\]]+)\]','<a title="Документ: %(word)s" href="%%40%%40searchpage.html?name.any_of:record:tuple=%(quote(word))s">%(title)s</a>'),
        ('name-reference-simple','\[name:(?P<word>[^\]]+)\]','<a title="Документ: %(word)s" href="%%40%%40searchpage.html?name.any_of:record:tuple=%(quote(word))s">%(word)s</a>'),
        ('reference','((?<=\s|>)|(?<=^))(?P<href>http://[^\s<]+)((?=\s|<|$))','<a href="%(href)s">%(href)s</a>'),
        ('st-reference','"(?P<title>[^:"]*)":(?P<href>[^:]+://\S+)','<a title="Ссылка на: %(href)s" href="%(href)s">%(title)s</a>'),
        ('st-reference-make','((?<=\s|>)|(?<=^))(?P<href>http://[^\s<]+)((?=\s|<|$))','"%(href)s":%(href)s'),
        ) :
        base[name] = ConverterRegexp(regexp,format)                        
        sm.registerUtility(base[name], provided=IConverterRegexp, name=name)

    base[u'asis'] = ConverterHead(
        regexp=u'(?ums)^(?P<body>.*)$',
        format=u'<pre>%(body)s</pre>',
        bytes=102400000,
        lines=100000            
        )
        
    sm.registerUtility(base[u'asis'], provided=IConverterHead, name=u'asis')        

    base[u'head'] = ConverterHead(
        regexp=u'(?ums)^\s*(?P<body>.{,1024})',
        format=u'<p>%(body)s ...</p>',
        bytes=1024,
        lines=1000000            
        )
        
    sm.registerUtility(base[u'head'], provided=IConverterHead, name=u'head')        

    base[u'annotator'] = ConverterAnnotator("""
      alt
      altlinux
      altlinux team
      apt
      apt-get
      bot
      btreecontainer
      btreefolder
      b-дерево
      cm
      corba
      daedalus
      distutils
      django
      dreambot
      easy_install
      factory
      five
      handler
      heapq
      invariant
      irequest
      keysolutions
      ks
      lazy
      lazy evaluation
      libxmlrpc
      namespace
      object root
      plone
      pypi
      pypo
      python
      python package index
      python policy
      python policy (pypo)
      rbn
      request
      rest
      restructured text
      robot
      ror
      rpas
      rpm
      rpm-build-python
      rst
      ruby
      rubyonrails
      ruby on rails
      self-organizingmap
      setuptools
      sisyphus
      sitemanager
      soap
      som
      subscriber
      subscribers
      traverse
      traversing
      ttw
      turing
      twisted
      websom
      widget
      xmlrpc
      xmlrpclib
      zc.buildout
      zcml
      zodb
      zope
      zope2
      zope3
      zope page template
      zpt
      адаптер
      адаптер вида
      адаптер пространства имен
      а́лан матисон тью́ринг 
      аннотация
      блокирующий вызов
      бот
      вид
      джанго
      дистанция левенштейна
      запрос
      инстанция zope
      инструмент
      интерфейс
      интерфейс-маркер
      канал
      канал событий
      ключевые решения
      компонент
      компонентная модель
      кр
      кс
      левенштейн
      ленивые вычисления
      мультиадаптер
      неймспейс
      обработчик события
      объект
      объекта
      ограничения
      ооп
      отложенные вычисления
      питон
      подписной адаптер
      поле
      поле схемы
      пространство имен
      рабочая область zope
      расстояние левенштейна
      реестр адаптеров
      реестр утилит
      сеть радиального базиса
      синхронный вызов
      скин
      схема
      схема интерефейса
      схема интерфейса
      траверс
      тьюринг
      утилита
      фабрика
      экземпляр zope
    """)
    sm.registerUtility(base[u'annotator'], provided=IConverterAnnotator, name=u'annotator')        

    base[u'converterrest'] = ConverterReST()
    sm.registerUtility(base[u'converterrest'], provided=IConverterReST, name=u'converterrest')        

    base[u'converterst'] = ConverterST()
    sm.registerUtility(base[u'converterst'], provided=IConverterST, name=u'converterst')        

    for name, chain in (
        ( u'converter:ANNOTATOR',( u'comment-killer', u'killrestchaptersign', u'annotator', u'head', u'keyword-reference', u'keyword-reference-simple', u'name-reference', u'name-reference-simple', u'reference', u'st-reference' )),
        ( u'converter:ASIS',( u'asis', u'keyword-reference', u'keyword-reference-simple', u'name-reference', u'name-reference-simple', u'st-reference' )),
        ( u'converter:AUTOSUMMARY',( u'converter:ANNOTATOR', u'absolute_url' )),
        ( u'converter:Export',( u'comment-killer', u'keyword-killer', u'keyword-killer-simple', u'name-killer', u'name-killer-simple', u'st-reference-make' )),
        ( u'converter:ReST+WIKI',( u'comment-killer', u'converterrest', u'degenerator', u'keyword-reference', u'keyword-reference-simple', u'name-reference', u'name-reference-simple', u'reference', u'st-reference', u'killdivabstractstyle' )),
        ( u'converter:ST+WIKI',( u'comment-killer', u'converterst', u'keyword-reference', u'keyword-reference-simple', u'name-reference', u'name-reference-simple', u'reference', u'st-reference' )),
        ( u'converter:SUMMARY',( u'converter:ST+WIKI', u'absolute_url' )),
        ) :

        converter[name] = ConverterChain()
        converter[name].chain = chain
        sm.registerUtility(converter[name], provided=IConverterChain, name=name)

    converter[u'converter:XSLT+SELECT'] = ConverterContainer()
    converter[u'converter:XSLT+SELECT']['0-ConverterXSLT'] = ConverterXSLT(html_charset='utf8')
    converter[u'converter:XSLT+SELECT']['1-ConverterSelect'] = ConverterSelect(
        dwin = 50,
        lwin = 100,
        threshold = 3,
    )

    sm.registerUtility(converter[u'converter:XSLT+SELECT'], provided=IConverterContainer, name=u'converter:XSLT+SELECT')

    sm[u'Cachestore'] = Cachestore()
    sm[u'Cachestore'].intIdsName= u'intid'
    sm.registerUtility(sm[u'Cachestore'], provided=ICachestore)

    return "Success"

def installMapper(context, **kw):
    """ Устанавливает MapperObject со всеми его внутренностями
    """

    sm = context.getSiteManager()

    mo = sm['converter'][u'MapperObject'] = MapperObject()

    sm.registerUtility(mo, provided=IMapperObject)

    names = (
       [u'ng.content.article.division.interfaces.IDivision',
        u'ng.app.converter.object2psadapter.interfaces.IPropertySheet',
        {
         u'abstract': (u'abstract',u'converter:ST+WIKI'),
         u'title': (u'title',u'reference'),
       }],
       [u'ng.content.article.interfaces.IDocFormatSwitcher',
        u'ng.app.converter.object2psadapter.interfaces.IPropertySheet',
        {
         u'abstract': (u'abstract',u'converter:ST+WIKI'),
         u'auto': (u'body',u'converter:ANNOTATOR'),
         u'autosummary': (u'body',u'converter:AUTOSUMMARY'),
         u'body': (u'body',u'converter:ASIS'),
         u'export': (u'body',u'converter:Export'),
         u'summary': (u'abstract',u'converter:SUMMARY'),
         u'title': (u'title',u'reference'),
       }],
       [u'ng.content.article.maincontainer.interfaces.IMainPage',
        u'ng.app.converter.object2psadapter.interfaces.IPropertySheet',
        {
         u'abstract': (u'abstract',u'converter:ST+WIKI'),
         u'title': (u'title',u'reference'),
       }],
       [u'ng.site.content.switcher.interfaces.IArticleASIS',
        u'ng.app.converter.object2psadapter.interfaces.IPropertySheet',
        {
         u'abstract': (u'abstract',u'converter:ST+WIKI'),
         u'auto': (u'body',u'converter:ANNOTATOR'),
         u'autosummary': (u'body',u'converter:AUTOSUMMARY'),
         u'body': (u'body',u'converter:ASIS'),
         u'export': (u'body',u'converter:Export'),
         u'summary': (u'abstract',u'converter:SUMMARY'),
         u'title': (u'title',u'reference'),
       }],
       [u'ng.site.content.switcher.interfaces.IArticleHTML',
        u'ng.app.converter.object2psadapter.interfaces.IPropertySheet',
        {
         u'abstract': (u'abstract',u'converter:ST+WIKI'),
         u'body': (u'body',u'converter:XSLT+SELECT'),
         u'export': (u'body',u'converter:Export'),
         u'title': (u'title',u'reference'),
       }],
       [u'ng.site.content.switcher.interfaces.IArticleREST',
        u'ng.app.converter.object2psadapter.interfaces.IPropertySheet',
        {
         u'abstract': (u'abstract',u'converter:ST+WIKI'),
         u'auto': (u'body',u'converter:ANNOTATOR'),
         u'autosummary': (u'body',u'converter:AUTOSUMMARY'),
         u'body': (u'body',u'converter:ReST+WIKI'),
         u'export': (u'body',u'converter:Export'),
         u'summary': (u'abstract',u'converter:SUMMARY'),
         u'title': (u'title',u'reference'),
       }],
       [u'ng.site.content.switcher.interfaces.IArticleST',
        u'ng.app.converter.object2psadapter.interfaces.IPropertySheet',
        {
         u'abstract': (u'abstract',u'converter:ST+WIKI'),
         u'auto': (u'body',u'converter:ANNOTATOR'),
         u'autosummary': (u'body',u'converter:AUTOSUMMARY'),
         u'body': (u'body',u'converter:ST+WIKI'),
         u'export': (u'body',u'converter:Export'),
         u'summary': (u'abstract',u'converter:SUMMARY'),
         u'title': (u'title',u'reference'),
       }],
    )
    
    for i in range(len(names)):
        mo[names[i][0]] = MapperInterface()
        mo[names[i][0]][names[i][1]] = MapperAttribute()
        for j in names[i][2].keys():
            mai = mo[names[i][0]][names[i][1]][j] = MapperAttributeItem()
            mai.attr = names[i][2][j][0]
            mai.converter = names[i][2][j][1]
    
    return "Success"
