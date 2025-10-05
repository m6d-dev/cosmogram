from src.apps.content.models.comment import Comment, PostComment
from src.apps.content.repositories.comment import CommentRepository, comment_repo
from src.apps.content.services.post_comment import post_comment_service
from src.utils.bases.services import AbstractService


class CommentService(AbstractService[Comment]):
    def __init__(self, repository: CommentRepository = comment_repo):
        super().__init__(repository)

    def create(self, **kwargs):
        instance = super().create(**kwargs)
        post_comment_service.create(post_id=instance.post.id, comment_id=instance.id)
        return instance

comment_service = CommentService()
