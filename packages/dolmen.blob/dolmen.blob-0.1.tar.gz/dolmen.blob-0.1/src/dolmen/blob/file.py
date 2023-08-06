# -*- coding: utf-8 -*-

from ZODB.blob import Blob
from ZODB.interfaces import BlobError
from dolmen.file import NamedFile
from dolmen.blob import IBlobFile, IFileStorage
from zope.interface import implements
from zope.component import queryMultiAdapter


class StorageError(Exception):
    """An error raised if the storage failed.
    """


class BlobFile(NamedFile):
    """A INameFile component using a ZODB Blob to store the data.
    """
    implements(IBlobFile)

    def __init__(self, data='', contentType='', filename=None):
        self._blob = Blob()
        NamedFile.__init__(self, data, contentType, filename)
        
    def __str__(self):
        return self.data

    def __len__(self):
        file = self._blob.open('r')
        try:
            file.seek(0, 2)
            result = file.tell()
        finally:
            file.close()
        return result

    getSize = __len__

    @apply
    def data():
        """The blob property using a IFileStorage adapter
        to write down the value.
        """
        def get(self):
            blob = self._blob.open('r')
            data = blob.read()
            blob.close()
            return data
        
        def set(self, value):
            stored = queryMultiAdapter((self._blob, value), IFileStorage)
            if stored is not True:
                raise StorageError(
                    "An error occured during the blob storage. Check the "
                    "value type (%r). This value should implement IFile, "
                    "IString or IUnicode (see `dolmen.builtins`)."
                    % value.__class__)

        return property(get, set)


    @property
    def physical_path(self):
        try:
            filename = self._blob.committed()
        except BlobError:
            # We retry, the data has now been commited
            # if possible by the ZODB blob.
            try:
                filename = self._blob.committed()
            except BlobError:
                # The retry failed, we return None.
                return None
        return filename
