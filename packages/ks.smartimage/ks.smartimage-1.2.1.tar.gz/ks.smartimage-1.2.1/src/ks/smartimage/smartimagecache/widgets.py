### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/) 
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/) 
# All right reserved, 2006-2007
#######################################################################

"""ScaleWidgets for the Zope 3 based smartimagecache package

$Id: widgets.py 35337 2008-05-28 09:01:39Z cray $
"""
__author__  = "Anton Oprya"
__license__ = "ZPL"
__version__ = "$Revision: 35337 $"
__date__ = "$Date: 2008-05-28 13:01:39 +0400 (Срд, 28 Май 2008) $"

from zope.app.form import CustomWidgetFactory
from zope.app.form.browser import ObjectWidget
from zope.app.form.browser import TupleSequenceWidget
from smartimagecache import Scale

ScaleWidget = CustomWidgetFactory(ObjectWidget,Scale)
ScalesWidget = CustomWidgetFactory(TupleSequenceWidget,subwidget=ScaleWidget)
                    
