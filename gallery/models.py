from __future__ import annotations

from pathlib import Path
from typing import Optional

from django.core.files.images import ImageFile
from django.db import models, connection, IntegrityError
from django.db.models import QuerySet
from django.utils.text import slugify
from faker import Faker

from gallery.constants import ImageType
from gallery.errors import ImageDoesNotExist, ImageAlreadyExists
from gallery.preview import PreviewService


class ImageManager(models.Manager["ImageModel"]):
    def get_by_id(
        self, id: int, image_type: Optional[ImageType] = None
    ) -> "ImageModel":
        image_type_condition = {"type": image_type} if image_type else {}
        try:
            return self.filter(**image_type_condition).get(id=id)
        except ImageModel.DoesNotExist as e:
            raise ImageDoesNotExist(image_id=id, image_type=image_type) from e

    def get_all(self) -> QuerySet["ImageModel"]:
        return self.all()

    def update_id(self, current_id: int, new_id: int) -> None:
        command = f"UPDATE {self.model._meta.db_table} SET id = %(new_id)s WHERE id = %(current_id)s;"
        params = {"current_id": current_id, "new_id": new_id}
        try:
            with connection.cursor() as cursor:
                cursor.execute(command, params)
        except IntegrityError as e:
            raise ImageAlreadyExists(image_id=new_id) from e


def _image_path(instance: "ImageModel", filename: str) -> str:
    random_human_name = slugify(Faker().name())
    return (
        f"images/{instance.type}/{random_human_name}/{random_human_name}_fullsize.jpg"
    )


def _preview_path(instance: "ImageModel", filename: str) -> str:
    image_name = instance.image_title
    return f"images/{instance.type}/{image_name}/{image_name}_preview.jpg"


class ImageModel(models.Model):
    type = models.CharField(
        max_length=50, choices=ImageType.choices, default=ImageType.HUMAN
    )
    _image = models.ImageField(upload_to=_image_path)
    preview = models.ImageField(blank=True, null=True, upload_to=_preview_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ImageManager()

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"

    def __str__(self) -> str:
        return f"Image [{self.id}] {self.image.name}"

    @property
    def image(self) -> ImageFile:
        return self._image

    @image.setter
    def image(self, value: ImageFile) -> None:
        self._image = value
        self._image_changed = True

    def save(self, *args, **kwargs) -> None:
        if getattr(self, "_image_changed", True):
            self.preview = PreviewService.create_preview_image(self.image)
            self._image_changed = False
        super().save(*args, **kwargs)

    def _update_image_field(self):
        """Set image field name"""

    @property
    def image_title(self) -> str:
        path = Path(self.image.name)
        return path.stem.replace("_fullsize", "")
