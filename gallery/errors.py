from gallery.constants import ImageType


class ImageDoesNotExist(Exception):
    MSG = "Image with id: '{image_id}' does not exist"
    MSG_WITH_TYPE = (
        "Image with id: '{image_id}' and type: '{image_type}' does not exist"
    )

    def __init__(self, image_id: int, image_type: ImageType | None = None) -> None:
        if image_type:
            message = self.MSG_WITH_TYPE.format(
                image_id=image_id, image_type=image_type
            )
        else:
            message = self.MSG.format(image_id=image_id)
        self.message = message
        super().__init__()


class ImageAlreadyExists(Exception):
    MSG = "Image with this id: '{image_id}' already exists"

    def __init__(self, image_id: int) -> None:
        self.message = self.MSG.format(image_id=image_id)
        super().__init__()
