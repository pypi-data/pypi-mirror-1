### -*- coding: utf-8 -*- #############################################
"""EditPhoto class for the Zope 3 based ng.app.photo package

$Id: editphoto.py 51654 2008-09-07 21:33:15Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51654 $"


from zope.interface import Interface
from ng.app.photo.interfaces import IPhotoEdit, IPhotoParam
from zope.schema import getFieldNames, getFields
from zope.schema.interfaces import IField
from zope.app.file.interfaces import IImage
from ng.app.photo.interfaces import IPhoto, IPhotoTool
import Image
import StringIO
from zope.app.zapi import getAdapter
from transaction import get
from zope.lifecycleevent import ObjectModifiedEvent
from zope.event import notify

class EditPhoto(object) :

    msgerrors = []

    def getData(self,*kv,**kw) :
        photoparam = getFieldNames(IPhotoParam)
        data = [ (x, getattr(self.context, x)) for x in photoparam]

        photoedit = getFields(IPhotoEdit)
        
        for field in photoedit.keys() :
            if field not in photoparam :
                data.append((field, IField(photoedit[field]).default))

        width, height = self.context.getImageSize()

        data.append((u'width', width))
        data.append((u'height', height))
        
        return data

    def setData(self, d, **kw) :
        self.msgerrors  = []
        photoparam = getFieldNames(IPhotoParam)
        photoedit = getFields(IPhotoEdit)
        img = Image.open(StringIO.StringIO(IPhoto(self.context).data))
        
        old_size = self.context.getImageSize()
        new_size = (d[u'width'], d[u'height'])
        
        angle = IField(photoedit[u'rotation']).default
        
        used_filters = d[u'filters']
        
        if d[u'rotation'] != 0:
            angle = d[u'rotation']
        
        if d[u'rotations'] :
            img =  img.transpose(getattr(Image,"ROTATE_%u" % d[u'rotations'])) 
            
        if (old_size != new_size) :
            if d['storeratio'] :
                r =  float(old_size[0]) / float(old_size[1])
                
                x_optimal = new_size[1] * r
                y_optimal = new_size[0] / r
                
                if (x_optimal < new_size[0]) :
                    new_size = (x_optimal, new_size[1])
                if (y_optimal < new_size[1]) :
                    new_size = (new_size[0], y_optimal)
                
            img = img.resize(new_size, resample = d[u'resample'])

        
        if IField(photoedit[u'rotation']).default != angle :
            img = img.rotate(-angle, resample = d[u'resample'])
        
        if IField(photoedit[u'hmirror']).default != d['hmirror'] :
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        
        if IField(photoedit[u'vmirror']).default != d['vmirror'] :
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
        
        for x in photoparam :
            setattr(self.context, x, d[x])
        
        output = StringIO.StringIO()

        try :
            if img.mode != d['mode'] :
                img = img.convert(d['mode'])
        except ValueError, msg :
            self.msgerrors.append(msg)
        else :                            
            self.context.mode = d['mode']        
            try :
                img.save(output, self.context.contentType.split("/")[1], quality = d[u'quality'])
            except IOError, msg :
                self.msgerrors.append(msg)
            else :        
                IPhoto(self.context).data = output.getvalue()

                if used_filters != () :
                    for used_filter in used_filters :
                        try :
                            getAdapter(self.context, IPhotoTool, name=used_filter).do()
                        except ValueError,msg :
                            self.msgerrors.append(msg)
                            get().abort() 
                            break                            

        notify(ObjectModifiedEvent(self.context))        
        return True
