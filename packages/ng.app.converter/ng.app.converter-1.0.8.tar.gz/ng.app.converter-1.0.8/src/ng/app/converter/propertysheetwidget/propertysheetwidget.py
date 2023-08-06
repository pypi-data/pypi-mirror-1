### -*- coding: utf-8 -*- #############################################
#######################################################################
"""PropertySheet Display Widget

$Id: propertysheetwidget.py 49773 2008-01-03 13:40:06Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49773 $"

from zope.app.form.interfaces import IDisplayWidget
from zope.app.form.browser.widget import DisplayWidget
from zope.interface import implements
from ng.app.converter.object2psadapter.interfaces import IPropertySheet

class PropertySheetDisplayWidget(DisplayWidget):

    implements (IDisplayWidget)
    def __call__(self):
        return IPropertySheet(self.context.context)[self.context.__name__]
