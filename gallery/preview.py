from io import BytesIO

from PIL import Image
from django.core.files.images import ImageFile

from gallery.constants import THUMBNAIL_MAX_HEIGHT, THUMBNAIL_MAX_WIDTH


class PreviewService:
    @classmethod
    def create_preview_image(
        cls,
        image: ImageFile,
        size: tuple[int, int] = (THUMBNAIL_MAX_HEIGHT, THUMBNAIL_MAX_WIDTH),
    ) -> ImageFile:
        """Return a thumbnail for given Image Field File"""
        img = Image.open(image.file)
        img.thumbnail(size=size)

        image_file = BytesIO()
        img.save(image_file, format="jpeg")
        image_file.seek(0)
        return ImageFile(image_file, name="this_person_does_not_exist_preview.jpg")
