from __future__ import annotations

from datetime import datetime
from typing import Self, TYPE_CHECKING, Optional

from django.db.models import QuerySet
from ninja import Schema
from pydantic import Field

from .constants import ITEMS_PER_PAGE, ImageType

if TYPE_CHECKING:
    from .models import ImageModel


class ErrorSchema(Schema):
    message: str


class LimitOffsetPaginationSchema(Schema):
    limit: int = Field(ITEMS_PER_PAGE, ge=1)
    offset: int = Field(0, ge=0)


class ImageBaseSchema(Schema):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        frozen = True


class FullSizeImageDetailsSchema(Schema):
    title: str
    url: str


class FullSizeImageSchema(ImageBaseSchema):
    image: FullSizeImageDetailsSchema

    @classmethod
    def from_model(cls, model: ImageModel) -> Self:
        return cls(
            id=model.id,
            image=FullSizeImageDetailsSchema(
                title=model.image_title, url=str(model.image.path)
            ),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class PreviewImageDetailsSchema(Schema):
    title: str
    url: Optional[str]


class PreviewImageSchema(ImageBaseSchema):
    image: PreviewImageDetailsSchema

    @classmethod
    def from_model(cls, model: ImageModel) -> Self:
        return cls(
            id=model.id,
            image=PreviewImageDetailsSchema(
                title=model.image_title,
                url=model.preview and str(model.preview.path) or None,
            ),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class PaginatedImagesSchema(Schema):
    items: list[PreviewImageSchema]
    count: int

    @classmethod
    def from_queryset(cls, images: QuerySet[ImageModel], count: int) -> Self:
        return cls(
            items=[PreviewImageSchema.from_model(model=image) for image in images],
            count=count,
        )


class UpdateImageSchema(Schema):
    image_new_id: int


class UploadImageSchema(Schema):
    id: int
    image_type: ImageType
