from src.apps.content.models.post import Post, PostImage
from src.utils.bases.repositories import AbstractRepository


class PostRepository(AbstractRepository[Post]):
    model = Post


class PostImageRepository(AbstractRepository[PostImage]):
    model = PostImage


post_repo = PostRepository()
post_image_repo = PostImageRepository()
