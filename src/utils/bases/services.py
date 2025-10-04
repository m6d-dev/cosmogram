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
    Mapping,
)

from django.db.models import QuerySet
from rest_framework import status

from src.utils.functions import raise_validation_error_detail


from .repositories import (
    AbstractEditRepository,
    AbstractFetchRepository,
    AbstractRepository,
)
from .types import TModel


class AbstractFetchService(Generic[TModel]):
    def __init__(self, repository: Union[AbstractFetchRepository]):
        self._repository = repository

    @property
    def model(self) -> TModel:
        return self._repository.model

    def get(self, *args, **kwargs) -> TModel:
        return self._repository.get(*args, **kwargs)

    def filter(self, *args, **kwargs) -> QuerySet[TModel]:
        return self._repository.filter(*args, **kwargs)

    def all(self) -> QuerySet[TModel]:
        return self._repository.all()

    def count(self, *args, **kwargs) -> int:
        return self._repository.count(*args, **kwargs)

    def exists(self, *args, **kwargs) -> bool:
        return self._repository.exists(*args, **kwargs)


class AbstractEditService(Generic[TModel]):
    def __init__(self, repository: AbstractEditRepository[TModel]):
        self._repository = repository

    @property
    def model(self) -> TModel:
        return self._repository.model

    def create(self, **kwargs) -> TModel:
        instance = self._create(**kwargs)
        instance.save()
        return instance

    def get_or_create(
        self, defaults: Optional[MutableMapping[str, Any]] = None, **kwargs
    ) -> Tuple[TModel, bool]:
        return self._repository.get_or_create(defaults=defaults, **kwargs)

    def _create(self, validate: bool = True, **kwargs) -> TModel:
        self.validate_fields(**kwargs)
        return self.model(**kwargs)  # noqa

    def update(self, **kwargs) -> TModel:
        return self._repository.update(**kwargs)

    def delete(self, instance) -> None:
        return self._repository.delete(instance)

    def save(self, instance: TModel, **kwargs):
        return self._repository.save(instance, **kwargs)

    def bulk_create_from_dict(
        self, data: Iterable[Mapping[str, Any]], **kwargs
    ) -> List[TModel]:
        instances = [self._create(**kwargs, **item) for item in data]
        return self._repository.bulk_create(instances)

    def bulk_create(self, instances: Sequence[TModel]) -> List[TModel]:
        return self._repository.bulk_create(instances)

    def bulk_update(
        self,
        instances: Sequence[TModel],
        fields: Sequence[str],
        batch_size: Optional[int] = None,
    ) -> int:
        return self._repository.bulk_update(
            instances=instances, fields=fields, batch_size=batch_size
        )

    def validate_fields(self, **kwargs) -> None:
        model_fields_names = {field.name for field in self.model._meta.fields}
        for field in kwargs.keys():
            if (
                field not in model_fields_names
                and field.removesuffix("_id") not in model_fields_names
            ):
                raise_validation_error_detail(
                    f"Model {self.model.__name__} has no field {field}"
                )

    def update_or_create(
        self, defaults: MutableMapping[str, Any], **kwargs
    ) -> Tuple[TModel, bool]:
        return self._repository.update_or_create(defaults=defaults, **kwargs)


class AbstractService(
    ABC, Generic[TModel], AbstractFetchService[TModel], AbstractEditService[TModel]
):
    @property
    def model(self) -> Type[TModel]:
        return self._repository.model

    def __init__(self, repository: Union[AbstractRepository[TModel]]):
        super().__init__(repository=repository)

    def raise_not_found(self, message: Optional[str] = None):
        message = message or f"{self.model._meta.verbose_name} не найдена"
        raise_validation_error_detail(message=message, code=status.HTTP_404_NOT_FOUND)
