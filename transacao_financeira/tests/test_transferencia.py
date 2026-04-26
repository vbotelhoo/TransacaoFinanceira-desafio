from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

import pytest

from transacao_financeira.domain.entities import Conta, Transacao
from transacao_financeira.domain.exceptions import SaldoInsuficienteError, ContaNaoEncontradaError
from transacao_financeira.repository.in_memory import InMemoryContaRepository
from transacao_financeira.services.transferencia import TransferenciaService


def make_service(*contas: Conta) -> TransferenciaService:
    return TransferenciaService(InMemoryContaRepository(list(contas)))


def make_transacao(origem: int, destino: int, valor: str, correlation_id: int = 1) -> Transacao:
    return Transacao(correlation_id, origem, destino, Decimal(valor))


class TestTransferenciaSaldoSuficiente:
    def test_debita_origem(self):
        service = make_service(Conta(1, Decimal("100")), Conta(2, Decimal("0")))
        service.transferir(make_transacao(1, 2, "60"))
        repo = service._repo
        assert repo.get_by_numero(1).saldo == Decimal("40")

    def test_credita_destino(self):
        service = make_service(Conta(1, Decimal("100")), Conta(2, Decimal("0")))
        service.transferir(make_transacao(1, 2, "60"))
        assert service._repo.get_by_numero(2).saldo == Decimal("60")

    def test_valor_exato_do_saldo(self):
        service = make_service(Conta(1, Decimal("100")), Conta(2, Decimal("0")))
        service.transferir(make_transacao(1, 2, "100"))
        assert service._repo.get_by_numero(1).saldo == Decimal("0")
        assert service._repo.get_by_numero(2).saldo == Decimal("100")


class TestTransferenciaSaldoInsuficiente:
    def test_levanta_excecao(self):
        service = make_service(Conta(1, Decimal("50")), Conta(2, Decimal("0")))
        with pytest.raises(SaldoInsuficienteError):
            service.transferir(make_transacao(1, 2, "51"))

    def test_saldo_origem_nao_alterado(self):
        service = make_service(Conta(1, Decimal("50")), Conta(2, Decimal("0")))
        with pytest.raises(SaldoInsuficienteError):
            service.transferir(make_transacao(1, 2, "51"))
        assert service._repo.get_by_numero(1).saldo == Decimal("50")

    def test_saldo_destino_nao_alterado(self):
        service = make_service(Conta(1, Decimal("50")), Conta(2, Decimal("0")))
        with pytest.raises(SaldoInsuficienteError):
            service.transferir(make_transacao(1, 2, "51"))
        assert service._repo.get_by_numero(2).saldo == Decimal("0")

    def test_mensagem_contem_correlation_id(self):
        service = make_service(Conta(1, Decimal("10")), Conta(2, Decimal("0")))
        with pytest.raises(SaldoInsuficienteError, match="42"):
            service.transferir(make_transacao(1, 2, "100", correlation_id=42))


class TestTransferenciaContaInexistente:
    def test_origem_inexistente(self):
        service = make_service(Conta(2, Decimal("100")))
        with pytest.raises(ContaNaoEncontradaError):
            service.transferir(make_transacao(999, 2, "10"))

    def test_destino_inexistente(self):
        service = make_service(Conta(1, Decimal("100")))
        with pytest.raises(ContaNaoEncontradaError):
            service.transferir(make_transacao(1, 999, "10"))


class TestTransferenciaConcorrencia:
    def test_saldo_consistente_sob_concorrencia(self):
        """Dispara 100 transferências de R$1 em paralelo; saldo total deve ser conservado."""
        contas = [Conta(1, Decimal("100")), Conta(2, Decimal("0"))]
        service = make_service(*contas)

        transacoes = [make_transacao(1, 2, "1", correlation_id=i) for i in range(100)]

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(service.transferir, t) for t in transacoes]
            for f in futures:
                f.result()

        repo = service._repo
        assert repo.get_by_numero(1).saldo == Decimal("0")
        assert repo.get_by_numero(2).saldo == Decimal("100")

    def test_sem_deadlock_locks_invertidos(self):
        """Threads com pares (A->B) e (B->A) simultâneos não devem travar."""
        contas = [Conta(1, Decimal("1000")), Conta(2, Decimal("1000"))]
        service = make_service(*contas)

        ab = [make_transacao(1, 2, "1", correlation_id=i) for i in range(50)]
        ba = [make_transacao(2, 1, "1", correlation_id=i + 50) for i in range(50)]

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(service.transferir, t) for t in ab + ba]
            for f in futures:
                f.result()

        repo = service._repo
        total = repo.get_by_numero(1).saldo + repo.get_by_numero(2).saldo
        assert total == Decimal("2000")
