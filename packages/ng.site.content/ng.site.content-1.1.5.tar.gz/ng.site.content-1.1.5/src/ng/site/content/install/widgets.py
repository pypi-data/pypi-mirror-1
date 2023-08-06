### -*- coding: utf-8 -*- #############################################
#######################################################################
""" Special widgets for ng.app.content.install addform

$Id: widgets.py 50586 2008-02-07 06:09:55Z corbeau $
"""
__author__  = u"Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 50586 $"


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
