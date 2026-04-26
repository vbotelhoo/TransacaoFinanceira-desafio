from decimal import Decimal

from transacao_financeira.domain.entities import Transacao
from transacao_financeira.domain.exceptions import SaldoInsuficienteError
from transacao_financeira.repository.interfaces import ContaRepository


class TransferenciaService:

    def __init__(self, repository: ContaRepository) -> None:
        self._repo = repository

    def transferir(self, transacao: Transacao) -> None:
        # Locks sempre adquiridos em ordem crescente de número de conta
        # para evitar deadlock entre threads que operam nos mesmos pares invertidos.
        first, second = sorted([transacao.conta_origem, transacao.conta_destino])
        lock_first = self._repo.get_lock(first)
        lock_second = self._repo.get_lock(second)

        with lock_first, lock_second:
            origem = self._repo.get_by_numero(transacao.conta_origem)
            destino = self._repo.get_by_numero(transacao.conta_destino)

            saldo_antes_origem = origem.saldo
            saldo_antes_destino = destino.saldo

            if origem.saldo < transacao.valor:
                raise SaldoInsuficienteError(
                    transacao.correlation_id,
                    origem.numero,
                    origem.saldo,
                    transacao.valor,
                )

            origem.debitar(transacao.valor)
            destino.creditar(transacao.valor)

            print(
                f"Transacao {transacao.correlation_id} efetivada | "
                f"Origem {origem.numero}: {saldo_antes_origem} -> {origem.saldo} | "
                f"Destino {destino.numero}: {saldo_antes_destino} -> {destino.saldo}"
            )
