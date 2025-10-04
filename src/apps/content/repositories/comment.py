from src.apps.content.models.comment import Comment, PostComment
from src.utils.bases.repositories import AbstractRepository


class CommentRepository(AbstractRepository[Comment]):
    model = Comment


class PostCommentRepository(AbstractRepository[PostComment]):
    model = PostComment


comment_repo = CommentRepository()
post_comment_repo = PostCommentRepository()
