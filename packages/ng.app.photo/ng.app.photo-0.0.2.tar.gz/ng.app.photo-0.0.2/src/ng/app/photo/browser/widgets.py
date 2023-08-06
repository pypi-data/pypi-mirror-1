### -*- coding: utf-8 -*- #############################################
#######################################################################
"""FilterWidget widget for the Zope 3 based ng.app.photo package

$Id: widgets.py 51654 2008-09-07 21:33:15Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51654 $"

from zope.app.form import CustomWidgetFactory
from zope.app.form.browser import TupleSequenceWidget

FiltersWidget = CustomWidgetFactory(
    TupleSequenceWidget
)
