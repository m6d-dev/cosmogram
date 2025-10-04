from src.apps.content.models.comment import PostComment
from src.apps.content.repositories.comment import (
    PostCommentRepository,
    post_comment_repo,
)
from src.utils.bases.services import AbstractService


class PostCommentService(AbstractService[PostComment]):
    def __init__(self, repository: PostCommentRepository = post_comment_repo):
        super().__init__(repository)


post_comment_service = PostCommentService()
