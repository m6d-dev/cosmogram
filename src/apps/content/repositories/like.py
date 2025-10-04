from src.apps.content.models.like import Like, PostLike
from src.utils.bases.repositories import AbstractRepository


class LikeRepository(AbstractRepository[Like]):
    model = Like


class PostLikeRepository(AbstractRepository[PostLike]):
    model = PostLike


like_repo = LikeRepository()
post_like_repo = PostLikeRepository()
