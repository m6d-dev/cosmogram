from abc import ABC, abstractmethod
from typing import Any, Union

from src.utils.bases.executable import AbstractExecutable
from src.utils.bases.types import TModel, TQuerySet


class AbstractUseCase(AbstractExecutable, ABC):
    @abstractmethod
    def __init__(self, **kwargs) -> None:
        pass

    @abstractmethod
    def execute(
        self, *args: object, **kwargs: object
    ) -> Union[TModel, TQuerySet, Any, None]:
        pass
