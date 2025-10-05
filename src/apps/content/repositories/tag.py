from src.apps.content.models.tag import Tag
from src.utils.bases.repositories import AbstractRepository


class TagRepository(AbstractRepository[Tag]):
    model = Tag

tag_repo = TagRepository()
