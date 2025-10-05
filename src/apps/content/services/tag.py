from src.apps.content.models.tag import Tag
from src.apps.content.repositories.tag import TagRepository, tag_repo
from src.utils.bases.services import AbstractService


class TagService(AbstractService[Tag]):
    def __init__(self, repository: TagRepository = tag_repo):
        super().__init__(repository)


tag_service = TagService()
