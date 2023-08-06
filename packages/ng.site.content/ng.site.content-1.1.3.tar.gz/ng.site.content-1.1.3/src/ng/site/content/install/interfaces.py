### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.site.content.install package

$Id: product.py 49265 2008-01-08 12:18:26Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49265 $"


from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime, Tuple, Object
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.file.interfaces import IImage
from zope.schema.interfaces import IField


class IRubricDescription(Interface) :

    name = TextLine(
        title=u'name',
        default=u'',
        required=True,
        )

    title = TextLine(
        title=u'Title',
        default=u'',
        required=False,
        )

    abstract = Text(
        title=u'Abstract',
        default=u'',
        required=False,
        )


class IInstall(Interface) :
    
    title = TextLine(title=u'title',
                           default=u'Dream Bot Site',
                           required=True)

    author  = TextLine(title=u'author',
                           default=u'Stepan Lomov',
                           required=True)


    article  = TextLine(title=u'Article title',
                               default=u'Публикации',
                               required=False)
                               
    about = TextLine(title=u'About title',
                           default=u'О проекте',
                           required=False)

    mirror = TextLine(title=u'Mirror title',
                              default=u'Зеркала',
                              required=False)

    dictionary = TextLine(title=u'Dictionary title',
                              default=u'Толковый словарь',
                              required=False)

    news = TextLine(title=u'News title',
                           default=u'Новости',
                           required=False)

    rubricator =  TextLine(title=u'Rubricator title',
                                 default=u'Рубрикатор',
                                 required=False)

    rubrics = Tuple(
        title=u'Site rubrics',
        description=u'Site rubrics',
        required=False,
        default=(),
        value_type=Object(title=u'site rubric', schema = IRubricDescription),
        )
        
    logo = Object(
        title = u"Logo",
        description = u"Logo",
        schema = IImage,
        )
