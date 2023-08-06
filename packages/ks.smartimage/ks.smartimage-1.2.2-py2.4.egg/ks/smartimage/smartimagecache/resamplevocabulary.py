### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################

"""ScaleWidgets for the Zope 3 based smartimagecache package

$Id: resamplevocabulary.py 35335 2008-05-27 16:02:13Z anatoly $
"""
__author__  = "Addrey Orlov"
__license__ = "ZPL"
__version__ = "$Revision: 35335 $"
__date__ = "$Date: 2008-05-27 19:02:13 +0300 (Tue, 27 May 2008) $"

from zope.schema.vocabulary import SimpleVocabulary

from PIL import Image

def ResampleVocabulary(context) :
    return SimpleVocabulary.fromItems(
         (
            ('NONE',    Image.NONE),
            ('ANTIALIAS', Image.ANTIALIAS),
            ('BILINEAR',  Image.BILINEAR),
            ('BICUBIC',   Image.BICUBIC)
         )
        )


