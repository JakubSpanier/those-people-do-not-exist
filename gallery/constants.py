from enum import StrEnum, auto
from typing import Final

THIS_PERSON_DOES_NOT_EXIST_URL: Final[str] = "https://thispersondoesnotexist.com"
THUMBNAIL_MAX_HEIGHT: Final[int] = 200
THUMBNAIL_MAX_WIDTH: Final[int] = 200
ITEMS_PER_PAGE: Final[int] = 20


class ImageType(StrEnum):
    HUMAN = auto()

    @classmethod
    def choices(cls):
        return tuple((img_type.name, img_type.value) for img_type in cls)
