
from atreal.filestorage.blobfile.fs import BlobDir

class BlobStore(BlobDir):
    title = "Blob File Store"
    def __init__(self, name, context):
        self.store_name = name
        self.context = context
        BlobDir.__init__(self, "", None)


