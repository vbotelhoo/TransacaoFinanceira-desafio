# TransacaoFinanceira-desafio

Solução para o desafio [TransacaoFinanceira](https://github.com/fnoriduki/TransacaoFinanceira)

### Estrutura

```text
transacao_financeira/
├── domain/
│   ├── entities.py       # Conta e Transacao
│   └── exceptions.py     # SaldoInsuficienteError, ContaNaoEncontradaError
├── repository/
│   ├── interfaces.py     # ContaRepository (ABC)
│   └── in_memory.py      # Implementação em memória com locks por conta
├── services/
│   └── transferencia.py  # TransferenciaService — lógica de transferência
├── tests/
│   ├── test_transferencia.py
│   └── test_repository.py
├── logging_config.py     # Configuração de logging (rich no terminal, JSON em produção)
└── main.py               # Execução com ThreadPoolExecutor
```

## Como executar

### Pré-requisitos

- Python 3.11+

### 1. Clonar e acessar o repositório

```bash
git clone <url-do-repositorio>
cd TransacaoFinanceira-desafio
```

### 2. Criar e ativar o ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows
```

### 3. Instalar o pacote com dependências de dev

```bash
pip install -e ".[dev]"
```

### 4. Rodar o código principal

```bash
python -m transacao_financeira.main
```

Por padrão o output usa o formato legível do `rich` com todos os campos de cada transferência. Para obter saída JSON (útil em CI/produção):

```bash
LOG_FORMAT=json python -m transacao_financeira.main
```

### 5. Rodar os testes

```bash
pytest
```

Com relatório de cobertura:

```bash
pytest --cov=transacao_financeira
```
