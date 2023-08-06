
import os
import tempfile

from StringIO import StringIO

from zope.interface import implements

from Products.blob.zopefile import OFSBlobFile

from atreal.filestorage.common.zodbstore import ZodbFile, ZodbDir
from atreal.filestorage.common.interfaces import IOmniFile

class BlobFile(ZodbFile):
    def __init__(self, name, parent, wrapFile=None):
        if wrapFile is None:
            wrapFile = OFSBlobFile("", "", StringIO())
        ZodbFile.__init__(self, name, parent, wrapFile)
    
    def open(self, mode='r'):
        return self.data.data.open(mode)
    
    #def displaceOnFS(self):
    #    self.lock = True
    #    file_obj = self.data.data.open()
    #    self.onFS = file_obj.name
    #    file_obj.close()
    #    return self.onFS

    def displaceOnFS(self):
        self.lock = True
        fd, self.onFS = tempfile.mkstemp(suffix=self.name)
        fs_file = os.fdopen(fd, 'w')
        
        file_obj = self.data.data.open('r')
        for chunk in file_obj:
            fs_file.write(chunk)
        
        fs_file.close()
        return self.onFS

    #def replaceFromFS(self):
    #    self.data._p_changed = True
    #    self.discardFromFS()
    #
    #def discardFromFS(self):
    #    del self.lock
    #    del self.onFS

class OfsBlobToOmni(BlobFile):
    implements(IOmniFile)
    def __init__(self, blob_file):
        BlobFile.__init__(self, blob_file.filename, None, blob_file)

    def setContentType(self, value):
        raise NotImplementedError

    def getContentType(self):
        return self.data.getContentType()


class BlobDir(ZodbDir):
    def makeFile(self, name):
        return self.makeChild(name, BlobFile)

    def makeDir(self, name):
        return self.makeChild(name, BlobDir)



