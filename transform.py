"""
Etapa de TRANSFORMAÇÃO (Transform) do pipeline ETL.

Recebe os dados brutos extraídos e aplica:
- Padronização de nomes de colunas
- Conversão de tipos (datas, floats)
- Cálculo de colunas derivadas (variação percentual diária, spread)
- Agregações (cotação média por semana)
"""
import pandas as pd


def transformar_cotacoes(df_bruto: pd.DataFrame) -> pd.DataFrame:
    df = df_bruto.copy()

    # Padroniza nomes de colunas (snake_case, comum em modelagem de dados)
    df = df.rename(columns={
        "cotacaoCompra": "cotacao_compra",
        "cotacaoVenda": "cotacao_venda",
        "dataHoraCotacao": "data_hora_cotacao",
    })

    # Conversão de tipos
    df["data_hora_cotacao"] = pd.to_datetime(df["data_hora_cotacao"])
    df["data"] = df["data_hora_cotacao"].dt.date
    df["cotacao_compra"] = pd.to_numeric(df["cotacao_compra"])
    df["cotacao_venda"] = pd.to_numeric(df["cotacao_venda"])

    # Remove duplicatas por data (mantém a última cotação do dia)
    df = df.sort_values("data_hora_cotacao").drop_duplicates(subset="data", keep="last")

    # Colunas derivadas
    df["spread"] = round(df["cotacao_venda"] - df["cotacao_compra"], 4)
    df["variacao_pct_dia_anterior"] = round(df["cotacao_venda"].pct_change() * 100, 2)

    # Classificação simples (útil para dashboards/BI depois)
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
    """Cria uma tabela agregada (cotação média semanal), simulando uma
    camada analítica típica de um Data Warehouse."""
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


if __name__ == "__main__":
    df_bruto = pd.read_csv("dados_brutos_extract.csv")
    df_transformado = transformar_cotacoes(df_bruto)
    df_agregado = gerar_agregado_semanal(df_transformado)

    df_transformado.to_csv("dados_transformados.csv", index=False, encoding="utf-8")
    df_agregado.to_csv("dados_agregado_semanal.csv", index=False, encoding="utf-8")

    print(f"[TRANSFORM] {len(df_transformado)} registros transformados.")
    print(f"[TRANSFORM] {len(df_agregado)} semanas agregadas.")
    print("\nAmostra dos dados transformados:")
    print(df_transformado.head())
