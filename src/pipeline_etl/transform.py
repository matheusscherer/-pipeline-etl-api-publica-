"""
Etapa de TRANSFORMAÇÃO (Transform) do pipeline ETL.

Padroniza colunas, converte tipos, calcula métricas derivadas e gera
agregação semanal (camada analítica).
"""
import pandas as pd


def transformar_cotacoes(df_bruto: pd.DataFrame) -> pd.DataFrame:
    df = df_bruto.copy()

    df = df.rename(columns={
        "cotacaoCompra": "cotacao_compra",
        "cotacaoVenda": "cotacao_venda",
        "dataHoraCotacao": "data_hora_cotacao",
    })

    df["data_hora_cotacao"] = pd.to_datetime(df["data_hora_cotacao"])
    df["data"] = df["data_hora_cotacao"].dt.date
    df["cotacao_compra"] = pd.to_numeric(df["cotacao_compra"])
    df["cotacao_venda"] = pd.to_numeric(df["cotacao_venda"])

    df = df.sort_values("data_hora_cotacao").drop_duplicates(subset="data", keep="last")

    df["spread"] = round(df["cotacao_venda"] - df["cotacao_compra"], 4)
    df["variacao_pct_dia_anterior"] = round(df["cotacao_venda"].pct_change() * 100, 2)

    df["tendencia"] = df["variacao_pct_dia_anterior"].apply(
        lambda x: "alta" if pd.notna(x) and x > 0
        else ("baixa" if pd.notna(x) and x < 0 else "estável")
    )

    df = df.reset_index(drop=True)
    df["id"] = df.index + 1

    colunas_finais = [
        "id", "data", "cotacao_compra", "cotacao_venda", "spread",
        "variacao_pct_dia_anterior", "tendencia", "fonte"
    ]
    return df[colunas_finais]


def gerar_agregado_semanal(df_transformado: pd.DataFrame) -> pd.DataFrame:
    """Camada analítica: cotação média / min / max por semana."""
    df = df_transformado.copy()
    df["data"] = pd.to_datetime(df["data"])
    df["ano_semana"] = df["data"].dt.strftime("%Y-S%U")

    agregado = df.groupby("ano_semana").agg(
        cotacao_media=("cotacao_venda", "mean"),
        cotacao_min=("cotacao_venda", "min"),
        cotacao_max=("cotacao_venda", "max"),
        dias_em_alta=("tendencia", lambda x: (x == "alta").sum()),
        dias_em_baixa=("tendencia", lambda x: (x == "baixa").sum()),
    ).reset_index()

    agregado["cotacao_media"] = agregado["cotacao_media"].round(4)
    return agregado
