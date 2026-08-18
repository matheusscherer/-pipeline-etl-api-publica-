"""
Etapa de CARGA (Load) do pipeline ETL.

Persiste os dados em SQLite com schema explícito:
- fato_cotacao_diaria (granularidade diária)
- agregado_cotacao_semanal (camada analítica)
"""
from datetime import datetime

import pandas as pd
import sqlite3


def carregar_no_banco(
    df_diario: pd.DataFrame,
    df_semanal: pd.DataFrame,
    caminho_db: str = "cotacoes.db",
) -> str:
    conn = sqlite3.connect(caminho_db)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fato_cotacao_diaria (
            id INTEGER PRIMARY KEY,
            data TEXT NOT NULL,
            cotacao_compra REAL,
            cotacao_venda REAL,
            spread REAL,
            variacao_pct_dia_anterior REAL,
            tendencia TEXT,
            fonte TEXT,
            carga_timestamp TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agregado_cotacao_semanal (
            ano_semana TEXT PRIMARY KEY,
            cotacao_media REAL,
            cotacao_min REAL,
            cotacao_max REAL,
            dias_em_alta INTEGER,
            dias_em_baixa INTEGER,
            carga_timestamp TEXT
        )
    """)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    df_diario = df_diario.copy()
    df_diario["carga_timestamp"] = timestamp
    df_semanal = df_semanal.copy()
    df_semanal["carga_timestamp"] = timestamp

    df_diario.to_sql("fato_cotacao_diaria", conn, if_exists="replace", index=False)
    df_semanal.to_sql("agregado_cotacao_semanal", conn, if_exists="replace", index=False)

    conn.commit()

    n_diario = cursor.execute("SELECT COUNT(*) FROM fato_cotacao_diaria").fetchone()[0]
    n_semanal = cursor.execute("SELECT COUNT(*) FROM agregado_cotacao_semanal").fetchone()[0]

    conn.close()

    print(f"[LOAD] {n_diario} registros carregados em 'fato_cotacao_diaria'.")
    print(f"[LOAD] {n_semanal} registros carregados em 'agregado_cotacao_semanal'.")
    print(f"[LOAD] Banco de dados: {caminho_db}")

    return caminho_db
