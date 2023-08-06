### -*- coding: utf-8 -*- #############################################
#######################################################################
"""PhotoToolFiltersVocabulary class for the Zope 3 based ng.app.photo package

$Id: phototoolfiltersvocabulary.py 51654 2008-09-07 21:33:15Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51654 $"


from zope.schema.vocabulary import SimpleVocabulary
from zope.app.zapi import getUtilitiesFor, getAdapters
from interfaces import IPhotoTool

def PhotoToolFiltersVocabulary(context):
    return SimpleVocabulary.fromValues([x for x,y in getAdapters([context], IPhotoTool, context=context)])
