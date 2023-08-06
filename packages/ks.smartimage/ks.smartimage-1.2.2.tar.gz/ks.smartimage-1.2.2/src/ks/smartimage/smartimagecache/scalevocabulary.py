### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/) 
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/) 
# All right reserved, 2006-2007
#######################################################################

"""ScaleWidgets for the Zope 3 based smartimagecache package

$Id: scalevocabulary.py 12472 2007-10-26 19:21:11Z anton $
"""
__author__  = "Addrey Orlov"
__license__ = "ZPL"
__version__ = "$Revision: 12472 $"
__date__ = "$Date: 2007-10-26 22:21:11 +0300 (Fri, 26 Oct 2007) $"

from zope.schema.vocabulary import SimpleVocabulary

def ScaleVocabulary(context) :
    return SimpleVocabulary.fromValues([ scale.name for scale in context.scales])

