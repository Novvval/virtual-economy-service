from abc import ABC, abstractmethod

from src.infrastructure.container import WriteContext, ReadContext


class UseCase(ABC):
    def __init__(self, context: WriteContext | ReadContext):
        self.ctx = context

    @abstractmethod
    def __call__(self, *args, **kwargs): ...
