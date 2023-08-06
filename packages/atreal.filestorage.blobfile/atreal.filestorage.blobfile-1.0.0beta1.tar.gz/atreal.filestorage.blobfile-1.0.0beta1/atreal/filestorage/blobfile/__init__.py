

from atreal.filestorage.common.registry import storage_classes
from atreal.filestorage.common.annotation import AnnotFileStore

from atreal.filestorage.blobfile.store import BlobStore

storage_classes['blob'] = BlobStore
AnnotFileStore.factory = BlobStore

