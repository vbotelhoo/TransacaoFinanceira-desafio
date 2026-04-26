class SaldoInsuficienteError(Exception):
    def __init__(self, correlation_id: int, conta: int, saldo: object, valor: object) -> None:
        super().__init__(
            f"Transacao {correlation_id} cancelada: conta {conta} tem saldo {saldo}, "
            f"insuficiente para transferir {valor}."
        )


class ContaNaoEncontradaError(Exception):
    def __init__(self, conta: int) -> None:
        super().__init__(f"Conta {conta} nao encontrada.")
