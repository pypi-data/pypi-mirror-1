### -*- coding: utf-8 -*- #############################################
#######################################################################
"""PhotoViewBase and PhotoNoCache classes for the Zope 3 based
ng.app.photo package

$Id: photoadapter.py 51654 2008-09-07 21:33:15Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51654 $"


from zope.publisher.browser import BrowserView
import time


class PhotoNoCache(BrowserView) :

    def __call__(self) :
        self.request.response.setHeader('Expires',
            time.strftime("%a, %d %b %Y %H:%M:%S GMT",time.gmtime(time.time())
            )
        )
        self.request.response.setHeader("Content-Type",self.context.contentType)
        return self.context.data
