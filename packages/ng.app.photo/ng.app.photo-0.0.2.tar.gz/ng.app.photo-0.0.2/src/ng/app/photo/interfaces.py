### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.app.photo package

$Id: interfaces.py 51654 2008-09-07 21:33:15Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51654 $"

from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime, Int, Tuple, Choice, Object
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.file.interfaces import IImage
from zope.schema.vocabulary import SimpleVocabulary
import Image

class IPhotoParamUniq(Interface) :

    mode = TextLine(
        title = u'Format',
        description = u'Image format',
        default = u'RGB',
        )

    quality = Int(
        title =u'Quality of Conversion (%)',
        default=90,
        min=0,
        max = 100,
    )

    resample = Choice(
        title = u'Resample Type',
        vocabulary = SimpleVocabulary.fromItems(
            (
             ('NONE',     Image.NONE    ), ('ANTIALIAS', Image.ANTIALIAS),
             ('BILINEAR', Image.BILINEAR), ('BICUBIC',   Image.BICUBIC)
            )
        ),
        required = True,
        default = Image.BICUBIC
    )


class IPhotoParam(IPhotoParamUniq) :

    contentType = TextLine(
        title = u'MIME type',
        description = u'MIME type of image',
        default = u'image/jpeg',
    )


class IPhotoEdit(IPhotoParam) :

    width = Int(
        title = u'Width',
        description = u'Image width',
        default = 0,
        min = 0,
        )

    height = Int(
        title = u'Height',
        description = u'Image height',
        default = 0,
        min = 0,
        )


    storeratio = Bool(
        title = u'Store ratio',
        description = u'Is need store ratio',
        default = True,
        )

    rotation = Int(
        title = u'Rotation angle',
        description = u'Rotation angle',
        default = 0,
        min = 0,
        max = 360,
        )

    rotations = Choice(
        title = u'Fixed rotation angle',
        description = u'Fixed rotation angle',
        vocabulary = SimpleVocabulary.fromValues([90, 180, 270]),
        required = False,
        )

    hmirror = Bool(
        title = u'Horizontal mirror',
        description = u'Is need horizontal mirror',
        default = False,
        )

    vmirror = Bool(
        title = u'Vertical mirror',
        description = u'Is need vertical mirror',
        default = False,
        )
    
    filters = Tuple(
        title = u'Filters',
        description = u'Filters that must be applied to image',
        value_type = Choice(vocabulary = 'PhotoToolFiltersVocabulary'),
        default = (),
    )


class IPhotoTool(Interface) :
    """ Do some modification of photo
    """
    
    def do() :
        """ Do something with photo
        """


class IPhoto(IPhotoParam, IImage, IContained) :
    """ Interface of Photo class
    """
