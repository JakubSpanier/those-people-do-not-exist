from http import HTTPStatus
from typing import TypeAlias

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpRequest, HttpResponse
from ninja import File, NinjaAPI, Query
from ninja.files import UploadedFile
from ninja.main import Exc

from .constants import ImageType
from .errors import ImageDoesNotExist, ImageAlreadyExists
from .models import ImageModel
from .schemas import (
    ErrorSchema,
    PaginatedImagesSchema,
    LimitOffsetPaginationSchema,
    FullSizeImageSchema,
    PreviewImageSchema,
    UpdateImageSchema,
    UploadImageSchema,
)


class SkyEngineAPI(NinjaAPI):
    def on_exception(self, request: HttpRequest, exc: Exc) -> HttpResponse:
        if isinstance(exc, ImageDoesNotExist):
            return self.create_response(
                request=request,
                status=HTTPStatus.NOT_FOUND,
                data=ErrorSchema(message=str(exc.message)),
            )

        return super().on_exception(request, exc)


api = SkyEngineAPI()

FullSizeImageResponseType: TypeAlias = tuple[
    HTTPStatus, FullSizeImageSchema | ErrorSchema
]
PreviewImageResponseType: TypeAlias = tuple[
    HTTPStatus, PreviewImageSchema | ErrorSchema
]
ImageListResponseType: TypeAlias = tuple[HTTPStatus, PaginatedImagesSchema]
UpdateImageResponseType: TypeAlias = tuple[HTTPStatus, None | ErrorSchema]


@api.get("/gallery/preview", response={HTTPStatus.OK: PaginatedImagesSchema})
def get_gallery(
    request: WSGIRequest, paginator: LimitOffsetPaginationSchema = Query(...)
) -> ImageListResponseType:
    """Returns a gallery of images"""
    images = ImageModel.objects.get_all()
    paginated_images = images[paginator.offset : paginator.offset + paginator.limit]
    return HTTPStatus.OK, PaginatedImagesSchema.from_queryset(
        images=paginated_images, count=images.count()
    )


@api.get(
    "/gallery/preview/{int:id}",
    response={HTTPStatus.OK: PreviewImageSchema, HTTPStatus.NOT_FOUND: ErrorSchema},
)
def get_preview(request: WSGIRequest, id: int) -> PreviewImageResponseType:
    """Returns a preview for a given ID"""
    image = ImageModel.objects.get_by_id(id=id)
    return HTTPStatus.OK, PreviewImageSchema.from_model(model=image)


@api.put(
    "/gallery/{int:id}",
    response={
        HTTPStatus.NO_CONTENT: None,
        HTTPStatus.BAD_REQUEST: ErrorSchema,
        HTTPStatus.NOT_FOUND: ErrorSchema,
    },
)
def update_image(
    request: WSGIRequest, id: int, data: UpdateImageSchema
) -> UpdateImageResponseType:
    """Update the image ID"""
    image = ImageModel.objects.get_by_id(id=id)
    try:
        ImageModel.objects.update_id(current_id=image.id, new_id=data.image_new_id)
    except ImageAlreadyExists as e:
        return HTTPStatus.BAD_REQUEST, ErrorSchema(message=str(e.message))
    return HTTPStatus.NO_CONTENT, None


@api.post(
    "/gallery/{int:id}",
    response={HTTPStatus.OK: FullSizeImageSchema, HTTPStatus.BAD_REQUEST: ErrorSchema},
)
def upload_image(
    request: WSGIRequest,
    id: int,
    data: UploadImageSchema,
    file: UploadedFile = File(...),
) -> FullSizeImageResponseType:
    """Upload an image for a given ID"""
    image = ImageModel.objects.get_by_id(id=id)
    image.type = data.image_type
    image.image = file
    image.save()
    return HTTPStatus.OK, FullSizeImageSchema.from_model(model=image)


@api.get(
    "/{image_type}/{int:id}",
    response={HTTPStatus.OK: FullSizeImageSchema, HTTPStatus.NOT_FOUND: ErrorSchema},
)
def get_image(
    request: WSGIRequest, image_type: ImageType, id: int
) -> FullSizeImageResponseType:
    """Returns a full-size image for a given ID"""
    image = ImageModel.objects.get_by_id(id=id, image_type=image_type)
    return HTTPStatus.OK, FullSizeImageSchema.from_model(model=image)
