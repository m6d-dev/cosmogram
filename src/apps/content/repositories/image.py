from src.apps.content.models.image import Image
from src.utils.bases.repositories import AbstractRepository


class ImageRepository(AbstractRepository[Image]):
    model = Image


image_repo = ImageRepository()
