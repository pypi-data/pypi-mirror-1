import os
from django.core.files import File
from django.core.files.storage import default_storage


class ImageImporter(object):

    def __init__(self, upload_to=None, storage=None):
        self.upload_to = upload_to
        self.storage = storage or default_storage

    def generate_filename(self, name):
        return os.path.join(self.upload_to, name)

    def import_image(self, name, content):
        return self.storage.save(name, content)

    def import_image_by_filename(self, filename, name=None):
        image_name = name or os.path.basename(filename)
        image_fh = open(filename, "rb")
        image_content = File(image_fh)
        return self.import_image(name, image_content)
