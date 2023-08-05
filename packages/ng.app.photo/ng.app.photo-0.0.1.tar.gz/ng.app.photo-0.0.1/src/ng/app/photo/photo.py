### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Photo class for the Zope 3 based ng.app.photo package

$Id: photo.py 49991 2008-02-08 18:41:27Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49991 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from zope.app import file
from zope.app.file.interfaces import IImage
from interfaces import IPhoto
from zope.app.container.contained import Contained
import Image


class Photo(file.image.Image, Contained) :

    implements(IPhoto)

    mode = u'RGB'
    
    quality = 90
    
    resample = Image.ANTIALIAS
