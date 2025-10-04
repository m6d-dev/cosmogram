from src.apps.content.models.post import Post
from src.apps.content.repositories.post import PostRepository, post_repo
from src.utils.bases.services import AbstractService


class PostService(AbstractService[Post]):
    def __init__(self, repository: PostRepository = post_repo):
        super().__init__(repository)


post_service = PostService()
