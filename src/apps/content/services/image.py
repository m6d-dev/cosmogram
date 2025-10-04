from src.apps.content.models.image import Image
from src.apps.content.repositories.image import ImageRepository, image_repo
from src.utils.bases.services import AbstractService


class ImageService(AbstractService[Image]):
    def __init__(self, repository: ImageRepository = image_repo):
        super().__init__(repository)


image_service = ImageService()
