from abc import ABC, abstractmethod
from threading import Lock

from transacao_financeira.domain.entities import Conta


class ContaRepository(ABC):

    @abstractmethod
    def get_by_numero(self, numero: int) -> Conta:
        ...

    @abstractmethod
    def get_lock(self, numero: int) -> Lock:
        ...
