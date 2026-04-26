import logging
from datetime import datetime
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed

from transacao_financeira.domain.entities import Conta, Transacao
from transacao_financeira.domain.exceptions import SaldoInsuficienteError, ContaNaoEncontradaError
from transacao_financeira.logging_config import configure_logging
from transacao_financeira.repository.in_memory import InMemoryContaRepository
from transacao_financeira.services.transferencia import TransferenciaService

logger = logging.getLogger(__name__)


CONTAS_INICIAIS: list[Conta] = [
    Conta(numero=938485762,  saldo=Decimal("180")),
    Conta(numero=347586970,  saldo=Decimal("1200")),
    Conta(numero=2147483649, saldo=Decimal("0")),
    Conta(numero=675869708,  saldo=Decimal("4900")),
    Conta(numero=238596054,  saldo=Decimal("478")),
    Conta(numero=573659065,  saldo=Decimal("787")),
    Conta(numero=210385733,  saldo=Decimal("10")),
    Conta(numero=674038564,  saldo=Decimal("400")),
    Conta(numero=563856300,  saldo=Decimal("1200")),
]

TRANSACOES: list[Transacao] = [
    Transacao(1, 938485762,  2147483649, Decimal("150"),  datetime(2023, 9, 9, 14, 15, 0)),
    Transacao(2, 2147483649, 210385733,  Decimal("149"),  datetime(2023, 9, 9, 14, 15, 5)),
    Transacao(3, 347586970,  238596054,  Decimal("1100"), datetime(2023, 9, 9, 14, 15, 29)),
    Transacao(4, 675869708,  210385733,  Decimal("5300"), datetime(2023, 9, 9, 14, 17, 0)),
    Transacao(5, 238596054,  674038564,  Decimal("1489"), datetime(2023, 9, 9, 14, 18, 0)),
    Transacao(6, 573659065,  563856300,  Decimal("49"),   datetime(2023, 9, 9, 14, 18, 20)),
    Transacao(7, 938485762,  2147483649, Decimal("44"),   datetime(2023, 9, 9, 14, 19, 0)),
    Transacao(8, 573659065,  675869708,  Decimal("150"),  datetime(2023, 9, 9, 14, 19, 1)),
]


def executar(service: TransferenciaService, transacao: Transacao) -> None:
    try:
        service.transferir(transacao)
    except SaldoInsuficienteError:
        logger.warning(
            "transferencia_cancelada",
            extra={
                "correlation_id": transacao.correlation_id,
                "conta_origem": transacao.conta_origem,
                "conta_destino": transacao.conta_destino,
                "valor": str(transacao.valor),
                "motivo": "saldo_insuficiente",
            },
        )
    except ContaNaoEncontradaError:
        logger.error(
            "transferencia_erro",
            extra={
                "correlation_id": transacao.correlation_id,
                "conta_origem": transacao.conta_origem,
                "conta_destino": transacao.conta_destino,
                "valor": str(transacao.valor),
                "motivo": "conta_nao_encontrada",
            },
        )


def main() -> None:
    configure_logging()
    repository = InMemoryContaRepository(CONTAS_INICIAIS)
    service = TransferenciaService(repository)

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(executar, service, t) for t in TRANSACOES]
        for future in as_completed(futures):
            future.result()


if __name__ == "__main__":
    main()
