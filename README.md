# 💱 Pipeline ETL — Cotação do Dólar (Banco Central)

Pipeline completo de **Extract, Transform, Load (ETL)** em Python, que
consome a API pública e oficial do **Banco Central do Brasil (PTAX)**,
transforma os dados (padronização, colunas derivadas, agregações) e
carrega em um banco SQL estruturado em camadas.

## Arquitetura do pipeline

```
┌───────────┐      ┌─────────────┐      ┌──────────┐
│  EXTRACT  │ ───► │  TRANSFORM  │ ───► │   LOAD   │
│ API do BCB│      │   Pandas    │      │  SQLite  │
└───────────┘      └─────────────┘      └──────────┘
```

- **Extract** (`extract.py`): busca a cotação diária do dólar (PTAX) na
  [API pública do Banco Central](https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata),
  sem necessidade de autenticação. Caso a API esteja indisponível, o
  script cai automaticamente em modo offline com dados sintéticos no
  mesmo formato, garantindo que o pipeline continue demonstrável.

- **Transform** (`transform.py`): padroniza nomes de colunas
  (`snake_case`), converte tipos, calcula colunas derivadas (spread,
  variação percentual, tendência) e gera uma camada agregada semanal —
  simulando a diferença entre uma tabela fato (granular) e uma tabela
  analítica (agregada) em um Data Warehouse.

- **Load** (`load.py`): cria o schema explícito no banco SQL e carrega
  duas tabelas: `fato_cotacao_diaria` e `agregado_cotacao_semanal`.

## Como rodar

```bash
# 1. Instale as dependências
pip install -r requirements.txt

# 2. Rode o pipeline completo (orquestra as 3 etapas)
python3 pipeline.py
```

Isso vai gerar o banco `cotacoes.db` com os dados extraídos, tratados e
carregados, além de imprimir no terminal um resumo de cada etapa e uma
validação final consultando o banco.

Também é possível rodar cada etapa isoladamente:

```bash
python3 extract.py     # gera dados_brutos_extract.csv
python3 transform.py   # gera dados_transformados.csv e dados_agregado_semanal.csv
python3 load.py        # carrega os CSVs no banco cotacoes.db
```

## Exemplo de saída

```
--- ETAPA 1: EXTRACT ---
[EXTRACT] 22 registros extraídos da API do Banco Central.

--- ETAPA 2: TRANSFORM ---
[TRANSFORM] 22 registros diários, 5 semanas agregadas.

--- ETAPA 3: LOAD ---
[LOAD] 22 registros carregados em 'fato_cotacao_diaria'.
[LOAD] 5 registros carregados em 'agregado_cotacao_semanal'.

Últimas 5 cotações carregadas:
  2026-08-14 | R$ 5.2126 | alta
  2026-08-13 | R$ 5.1967 | alta
  ...
```

## Estrutura do projeto

```
pipeline-etl-api-publica/
├── extract.py       # Etapa 1: extração da API do Banco Central
├── transform.py      # Etapa 2: limpeza, padronização e agregação
├── load.py           # Etapa 3: carga estruturada em SQLite
├── pipeline.py        # Orquestrador — roda as 3 etapas em sequência
├── requirements.txt
└── README.md
```

## Stack técnica

- **Python 3** — linguagem principal
- **Requests** — consumo de API REST
- **Pandas** — transformação e agregação de dados
- **SQLite** — camada de armazenamento estruturado (Data Warehouse simplificado)

## Possíveis evoluções

- Trocar SQLite por PostgreSQL/SQL Server para um cenário mais próximo de produção
- Adicionar orquestração com Airflow para execução agendada
- Expandir para múltiplas moedas (Euro, Libra) usando a mesma API do BCB
- Conectar ao [dashboard-analise-dados](../dashboard-analise-dados) para visualização

---

Desenvolvido por **Matheus Scherer** — [github.com/matheusscherer](https://github.com/matheusscherer)
