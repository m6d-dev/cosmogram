from abc import ABC
from typing import (
    Any,
    Generic,
    Iterable,
    MutableMapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
    List,
)
from django.db import models
from src.utils.functions import raise_validation_error
from src.utils.bases.types import TModel


class AbstractFetchRepository(Generic[TModel]):
    model: Type[TModel]

    @property
    def table_name(self) -> str:
        return self.model._meta.db_table

    def get(self, *args, **kwargs) -> Union[TModel, None]:
        res = self.filter(*args, **kwargs)
        if res.count() > 1:
            raise_validation_error("Multiple objects found")
        return res.first()

    def filter(self, *args, **kwargs) -> models.QuerySet[TModel]:
        return self.all().filter(*args, **kwargs)

    def all(self) -> models.QuerySet[TModel]:
        return self.model.objects.all()

    def count(self, *args, **kwargs) -> int:
        return self.filter(*args, **kwargs).count()

    def exists(self, *args, **kwargs) -> bool:
        return self.filter(*args, **kwargs).exists()


class AbstractEditRepository(Generic[TModel]):
    model: Type[TModel]

    def create(self, **kwargs) -> TModel:
        return self.model.objects.create(**kwargs)

    def update_or_create(
        self, defaults: Optional[MutableMapping[str, Any]] = None, **kwargs
    ) -> Tuple[TModel, bool]:
        return self.model.objects.update_or_create(defaults=defaults, **kwargs)

    def get_or_create(
        self, defaults: Optional[MutableMapping[str, Any]] = None, **kwargs
    ) -> Tuple[TModel, bool]:
        return self.model.objects.get_or_create(defaults=defaults, **kwargs)

    @staticmethod
    def update(instance: TModel, **kwargs) -> TModel:
        instance.save(**kwargs)
        return instance

    @staticmethod
    def delete(instance: TModel):
        instance.delete()

    @staticmethod
    def save(instance: TModel, **kwargs):
        instance.save(**kwargs)

    def bulk_create(self, instances: Iterable[TModel], **kwargs) -> List[TModel]:
        return self.model.objects.bulk_create(instances, **kwargs)

    def bulk_update(
        self,
        instances: Iterable[TModel],
        fields: Sequence[str],
        batch_size: Optional[int],
    ) -> int:
        return self.model.objects.bulk_update(
            objs=instances, fields=fields, batch_size=batch_size
        )

    def create_or_update(self, **kwargs) -> Tuple[TModel, bool]:
        instance, created = self.model.objects.update_or_create(**kwargs)
        return instance, created


class AbstractRepository(
    Generic[TModel],
    AbstractFetchRepository[TModel],
    AbstractEditRepository[TModel],
    ABC,
):
    def update_with_query(self, data: dict, **filters) -> int:
        return self.filter(**filters).update(**data)

    def delete_with_query(self, **filters) -> tuple[int, dict[str, int]]:
        return self.filter(**filters).delete()
