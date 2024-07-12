from http import HTTPStatus
from typing import Any

import requests
from io import BytesIO
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand, CommandParser

from gallery.constants import THIS_PERSON_DOES_NOT_EXIST_URL
from gallery.models import ImageModel


class Command(BaseCommand):
    help = "Download images from https://thispersondoesnotexist.com and save them in the database."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "num_images", type=int, help="The number of images to download", default=1
        )

    def handle(self, num_images, **kwargs: Any) -> None:
        self.stdout.write("Entering the download human images command...")

        for _ in range(num_images):
            self._download_image()

    def _download_image(self) -> None:
        response = requests.get(THIS_PERSON_DOES_NOT_EXIST_URL)
        if response.status_code == HTTPStatus.OK:
            img = ImageFile(
                BytesIO(response.content), name=f"this_person_does_not_exist.jpg"
            )
            ImageModel.objects.create(image=img)

            self.stdout.write(self.style.SUCCESS(f"Successfully downloaded image"))
        else:
            self.stdout.write(self.style.ERROR(f"Failed to download image"))
