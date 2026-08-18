# Pipeline ETL — Cotação do Dólar (Banco Central)

Pipeline completo de **Extract → Transform → Load** em Python que consome a API pública oficial do **Banco Central do Brasil (PTAX)**, transforma os dados e carrega em SQLite com schema estruturado.

> Projeto de portfólio focado em demonstrar maturidade em ETL, Pandas, consumo de API pública e boas práticas de engenharia.

---

## Arquitetura

```text
┌───────────┐      ┌─────────────┐      ┌──────────┐
│  EXTRACT  │ ───► │  TRANSFORM  │ ───► │   LOAD   │
│ API do BCB│      │   Pandas    │      │  SQLite  │
└───────────┘      └─────────────┘      └──────────┘
```

- **Extract**: cotação diária do dólar (PTAX). Fallback offline com dados sintéticos.
- **Transform**: padronização (`snake_case`), tipagem, spread, variação %, tendência + agregação semanal.
- **Load**: tabelas `fato_cotacao_diaria` e `agregado_cotacao_semanal`.

---

## Estrutura

```text
pipeline-etl-api-publica/
├── src/
│   └── pipeline_etl/
│       ├── __init__.py
│       ├── extract.py
│       ├── transform.py
│       ├── load.py
│       └── pipeline.py
├── tests/
│   ├── test_extract.py
│   └── test_transform.py
├── .github/workflows/ci.yml
├── pyproject.toml
├── README.md
└── LICENSE
```

---

## Instalação

```bash
git clone https://github.com/matheusscherer/-pipeline-etl-api-publica-.git
cd -pipeline-etl-api-publica-

python -m venv .venv
source .venv/bin/activate   # Linux/macOS

pip install -e ".[dev]"
```

---

## Como rodar

```bash
# Pipeline completo
python -m pipeline_etl.pipeline
# ou
pipeline-etl
```

O script gera `cotacoes.db` e imprime resumo de cada etapa + validação final.

---

## Testes

```bash
pytest -v
pytest --cov=pipeline_etl --cov-report=term-missing
```

---

## Stack

- Python 3.10+
- Requests (API REST)
- Pandas (transformação e agregação)
- SQLite (Data Warehouse simplificado)
- pytest + GitHub Actions

---

## Possíveis evoluções

- Trocar SQLite por PostgreSQL
- Orquestração com Airflow / Prefect
- Suporte a múltiplas moedas
- Dashboard de visualização

---

**Matheus Scherer** · [github.com/matheusscherer](https://github.com/matheusscherer)

MIT License
