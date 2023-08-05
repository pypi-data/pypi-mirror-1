### -*- coding: utf-8 -*- #############################################
#######################################################################
"""FilterWidget widget for the Zope 3 based ng.app.photo package

$Id: widgets.py 49991 2008-02-08 18:41:27Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49991 $"

from zope.app.form import CustomWidgetFactory
from zope.app.form.browser import TupleSequenceWidget

FiltersWidget = CustomWidgetFactory(
    TupleSequenceWidget
)
