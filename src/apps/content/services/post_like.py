from src.apps.content.models.like import PostLike
from src.apps.content.repositories.like import PostLikeRepository, post_like_repo
from src.utils.bases.services import AbstractService


class PostLikeService(AbstractService[PostLike]):
    def __init__(self, repository: PostLikeRepository = post_like_repo):
        super().__init__(repository)


post_like_service = PostLikeService()
