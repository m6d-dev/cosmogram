from src.apps.content.models.comment import Comment
from src.apps.content.repositories.comment import CommentRepository, comment_repo
from src.utils.bases.services import AbstractService


class CommentService(AbstractService[Comment]):
    def __init__(self, repository: CommentRepository = comment_repo):
        super().__init__(repository)


comment_service = CommentService()
