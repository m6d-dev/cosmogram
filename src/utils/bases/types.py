import typing
from typing import Generator, Sequence, Tuple, TypeAlias, TypeVar, Union

from django.db import models

T = TypeVar("T")
TModel = TypeVar("TModel", bound=models.Model)
TQuerySet = TypeVar("TQuerySet", bound=models.QuerySet[TModel])

SingleOrSequence: TypeAlias = Union[T, Sequence[T]]

ModelUpdateResult: TypeAlias = Tuple[TModel, typing.Iterable[str]]

# UNION_ENTITY_T: TypeAlias = Union[]

ModelUpdateResultFlow: TypeAlias = Generator[
    ModelUpdateResult,
    None,
    None,
]
