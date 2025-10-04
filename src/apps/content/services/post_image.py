from src.apps.content.models.post import PostImage
from src.apps.content.repositories.post import PostImageRepository, post_image_repo
from src.utils.bases.services import AbstractService


class PostImageService(AbstractService[PostImage]):
    def __init__(self, repository: PostImageRepository = post_image_repo):
        super().__init__(repository)


post_image_service = PostImageService()
