from decimal import Decimal
from threading import Lock

import pytest

from transacao_financeira.domain.entities import Conta
from transacao_financeira.domain.exceptions import ContaNaoEncontradaError
from transacao_financeira.repository.in_memory import InMemoryContaRepository


def make_repo(*contas: Conta) -> InMemoryContaRepository:
    return InMemoryContaRepository(list(contas))


class TestGetByNumero:
    def test_retorna_conta_existente(self):
        repo = make_repo(Conta(1, Decimal("100")))
        conta = repo.get_by_numero(1)
        assert conta.numero == 1
        assert conta.saldo == Decimal("100")

    def test_levanta_excecao_conta_inexistente(self):
        repo = make_repo(Conta(1, Decimal("100")))
        with pytest.raises(ContaNaoEncontradaError):
            repo.get_by_numero(999)

    def test_mensagem_contem_numero_da_conta(self):
        repo = make_repo()
        with pytest.raises(ContaNaoEncontradaError, match="42"):
            repo.get_by_numero(42)

    def test_retorna_mesma_instancia(self):
        """Repositório deve retornar a instância mutável, não uma cópia."""
        conta = Conta(1, Decimal("100"))
        repo = make_repo(conta)
        assert repo.get_by_numero(1) is conta


class TestGetLock:
    def test_retorna_lock_para_conta_existente(self):
        repo = make_repo(Conta(1, Decimal("0")))
        lock = repo.get_lock(1)
        assert isinstance(lock, type(Lock()))

    def test_levanta_excecao_lock_conta_inexistente(self):
        repo = make_repo(Conta(1, Decimal("0")))
        with pytest.raises(ContaNaoEncontradaError):
            repo.get_lock(999)

    def test_mesmo_lock_em_chamadas_repetidas(self):
        """Deve retornar sempre o mesmo objeto Lock para a mesma conta."""
        repo = make_repo(Conta(1, Decimal("0")))
        assert repo.get_lock(1) is repo.get_lock(1)

    def test_locks_distintos_por_conta(self):
        repo = make_repo(Conta(1, Decimal("0")), Conta(2, Decimal("0")))
        assert repo.get_lock(1) is not repo.get_lock(2)


class TestInicializacao:
    def test_multiplas_contas(self):
        repo = make_repo(
            Conta(1, Decimal("100")),
            Conta(2, Decimal("200")),
            Conta(3, Decimal("300")),
        )
        assert repo.get_by_numero(1).saldo == Decimal("100")
        assert repo.get_by_numero(2).saldo == Decimal("200")
        assert repo.get_by_numero(3).saldo == Decimal("300")

    def test_repositorio_vazio(self):
        repo = make_repo()
        with pytest.raises(ContaNaoEncontradaError):
            repo.get_by_numero(1)

    def test_numero_conta_grande(self):
        """Número acima de Int32.MaxValue deve funcionar normalmente."""
        repo = make_repo(Conta(2147483649, Decimal("0")))
        assert repo.get_by_numero(2147483649).numero == 2147483649
