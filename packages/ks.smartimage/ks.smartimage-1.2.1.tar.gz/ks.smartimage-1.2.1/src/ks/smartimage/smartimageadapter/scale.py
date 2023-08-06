### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Image scale method class for the Zope 3 based smartimage package

$Id: scale.py 35337 2008-05-28 09:01:39Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "ZPL"
__version__ = "$Revision: 35337 $"
__date__ = "$Date: 2008-05-28 13:01:39 +0400 (Срд, 28 Май 2008) $"

from zope.interface import Interface
from interfaces import IScaleError
from zope.interface import implements
from PIL import Image
import StringIO



class ScaleError(Exception) :
    implements(IScaleError)

    def __init__(self, sizein, sizeout, ratio, msg) :
        Exception.__init__(self,msg)
        self.sizein = sizein
        self.sizeout = sizeout
        self.ratio = ratio
        self.msg = msg



def scale(body,mode,format,x,y,ratio,resample,quality) :
    "resize image"
    im = Image.open(StringIO.StringIO(body))
    x1,y1 = im.size
    x2 = float(x)
    y2 = float(y)
    if max(x1/x,x/x1,y1/y,y2/y) > ratio :
        msg = "Image ratio are to big %s %s %s %s" % (float(x1)/float(x),
                                                      float(x)/float(x1),
                                                      float(y1)/float(y),
                                                      float(y)/float(y1))
        raise ScaleError((x1,y1),(x,y),ratio,msg)
    if x1 > x or y1 > y or im.format != format :
      x2 = float(x)
      y2 = float(y)
      if max(x1/x,x/x1,y1/y,y2/y) > ratio :
          msg = "Image ratio are to big %s %s %s %s" % (float(x1)/float(x),
                                                        float(x)/float(x1),
                                                        float(y1)/float(y),
                                                        float(y)/float(y1))
          raise ScaleError((x1,y1),(x,y),ratio,msg)


      im.thumbnail((x,y),resample=resample)
      im=im.convert(mode)
      output = StringIO.StringIO()
      im.save(output,format,quality=quality)

      return output.getvalue()
    return body
