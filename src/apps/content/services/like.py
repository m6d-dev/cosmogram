from src.apps.content.models.like import Like
from src.apps.content.repositories.like import LikeRepository, like_repo
from src.apps.content.services.post_like import post_like_service
from src.utils.bases.services import AbstractService
from django.db import transaction

class LikeService(AbstractService[Like]):
    def __init__(self, repository: LikeRepository = like_repo):
        super().__init__(repository)

    @transaction.atomic
    def create(self, **kwargs):
        instance = super().create(**kwargs)
        post_like_service.create(post_id=kwargs.get("post_id"), like=instance)
        return instance

    @transaction.atomic
    def delete(self, instance, *args, **kwargs):
        post_like_service.filter(post=kwargs.get("post_id"), like=instance).delete()
        return super().delete(instance)

like_service = LikeService()
