import os

from django.db.models.fields.files import ImageFieldFile, FieldFile
from django.core.files.storage import FileSystemStorage

from .backends.metadata import DatabaseBackend


class SourceImage(ImageFieldFile):

    def __init__(self, name):
        self.name = name


class ThumbnailedImageFile(FieldFile):

    def __init__(self, *args, **kwargs):
        super(ThumbnailedImageFile, self).__init__(*args, **kwargs)
        self.backend = DatabaseBackend()
        self.storage = FileSystemStorage()
        self.backend.add_source(self.name)

    def _get_thumbnail_name(self, size):
        filename, extension = os.path.splitext(self.name)
        return "%s_%s%s" % (filename, size, extension)

    def get_thumbnail(self, size):
        # 1. Get thumbnail from meta store
        # 2. If it doesn't exist, create thumbnail and return it
        thumbnail = self.backend.get_thumbnail(self.name, size)
        if thumbnail is None:
            return self.create_thumbnail(size)
        return thumbnail

    def create_thumbnail(self, size):
        # 1. Use Storage API to create a thumbnail (and get its filename)
        # 2. Call metadata_storage.add_thumbnail(self.name, size, filename)
        filename = self._get_thumbnail_name(size)
        self.storage.save(filename, self.file)
        return self.backend.add_thumbnail(self.name, size, filename)


    def delete_thumbnail(self, size):
        # 1. Use Storage API to delete thumbnail
        # 2. Call metadata_storage.remove_thumbnail(self.name, size)
        self.storage.delete(self._get_thumbnail_name(size))
        self.backend.delete_thumbnail(self.name, size)
