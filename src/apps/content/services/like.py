from src.apps.content.models.like import Like
from src.apps.content.repositories.like import LikeRepository, like_repo
from src.utils.bases.services import AbstractService


class LikeService(AbstractService[Like]):
    def __init__(self, repository: LikeRepository = like_repo):
        super().__init__(repository)


like_service = LikeService()
