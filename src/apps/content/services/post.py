from typing import Any, List
from src.apps.content.models.post import Post, PostImage
from src.apps.content.services.image import image_service
from src.apps.content.repositories.post import PostRepository, post_repo
from src.utils.bases.services import AbstractService
from src.apps.content.services.post_image import post_image_service


class PostService(AbstractService[Post]):
    def __init__(self, repository: PostRepository = post_repo):
        super().__init__(repository)

    def create(self, **kwargs):
        images = kwargs.pop("images")
        instance = super().create(**kwargs)
        self._set_images(instance=instance, images=images)
        return instance

    def _set_images(self, instance: Post, images: List[Any]):
        img_instances = [image_service.create(image=img) for img in images]
        post_image_service.bulk_create(
            [PostImage(post=instance, image=img_obj) for img_obj in img_instances]
        )


post_service = PostService()
