from decimal import Decimal
from threading import Lock

from transacao_financeira.domain.entities import Conta
from transacao_financeira.domain.exceptions import ContaNaoEncontradaError
from transacao_financeira.repository.interfaces import ContaRepository


class InMemoryContaRepository(ContaRepository):

    def __init__(self, contas: list[Conta]) -> None:
        self._contas: dict[int, Conta] = {c.numero: c for c in contas}
        self._locks: dict[int, Lock] = {c.numero: Lock() for c in contas}

    def get_by_numero(self, numero: int) -> Conta:
        conta = self._contas.get(numero)
        if conta is None:
            raise ContaNaoEncontradaError(numero)
        return conta

    def get_lock(self, numero: int) -> Lock:
        lock = self._locks.get(numero)
        if lock is None:
            raise ContaNaoEncontradaError(numero)
        return lock
