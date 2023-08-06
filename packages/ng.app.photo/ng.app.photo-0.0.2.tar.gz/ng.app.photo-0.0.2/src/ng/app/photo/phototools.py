### -*- coding: utf-8 -*- #############################################
#######################################################################
"""PhotoToolBase, PhotoToolBlur and PhotoToolEmboss classes for the
Zope 3 based ng.app.photo package

$Id: phototools.py 51654 2008-09-07 21:33:15Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51654 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from interfaces import IPhoto, IPhotoTool
from zope.component import adapts
import ImageFilter
import Image
import StringIO

#BLUR, CONTOUR, DETAIL, EDGE_ENHANCE, EDGE_ENHANCE_MORE, EMBOSS, FIND_EDGES,
#SMOOTH, SMOOTH_MORE, SHARPEN.


class PhotoToolBase(object) :

    implements(IPhotoTool)
    adapts(IPhoto)
    
    used_filter = None

    def __init__(self, context) :
        self.context = context

    def do(self) :
        """ Modify photo using some filter
        """
        img = Image.open(StringIO.StringIO(IPhoto(self.context).data))
        img = img.filter(self.used_filter)
        output = StringIO.StringIO()
        img.save(output, self.context.contentType.split("/")[1])
        IPhoto(self.context).data = output.getvalue()


class PhotoToolBlur(PhotoToolBase) :

    used_filter = ImageFilter.BLUR


class PhotoToolEmboss(PhotoToolBase) :

    used_filter = ImageFilter.EMBOSS
