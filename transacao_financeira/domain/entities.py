from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass
class Conta:
    numero: int
    saldo: Decimal

    def debitar(self, valor: Decimal) -> None:
        self.saldo -= valor

    def creditar(self, valor: Decimal) -> None:
        self.saldo += valor


@dataclass
class Transacao:
    correlation_id: int
    conta_origem: int
    conta_destino: int
    valor: Decimal
    datetime: datetime = field(default_factory=datetime.now)
