### -*- coding: utf-8 -*- #############################################
#######################################################################
"""PropertySheet Display Widget

$Id: propertysheetwidget.py 49320 2008-01-09 20:05:51Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49320 $"

from zope.app.form.interfaces import IDisplayWidget
from zope.app.form.browser.widget import DisplayWidget
from zope.interface import implements
from ng.app.converter.object2psadapter.interfaces import IPropertySheet

class PropertySheetDisplayWidget(DisplayWidget):

    implements (IDisplayWidget)
    def __call__(self):
        return IPropertySheet(self.context.context)[self.context.__name__]
