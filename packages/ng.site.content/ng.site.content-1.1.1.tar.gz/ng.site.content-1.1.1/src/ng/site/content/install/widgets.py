### -*- coding: utf-8 -*- #############################################
#######################################################################
""" Special widgets for ng.app.content.install addform

$Id: widgets.py 51196 2008-06-26 14:16:21Z cray $
"""
__author__  = u"Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51196 $"


from zope.app.form import CustomWidgetFactory
from ng.lib.objectwidget import ObjectWidget
from zope.app.form.browser import TupleSequenceWidget
from zope.app.file.image import Image
from rubricdescription import RubricDescription


LogoWidget = CustomWidgetFactory(
    ObjectWidget,
    Image
    )


RubricWidget = CustomWidgetFactory(
    TupleSequenceWidget,
    subwidget=CustomWidgetFactory(
        ObjectWidget,
        RubricDescription
        )
    )
