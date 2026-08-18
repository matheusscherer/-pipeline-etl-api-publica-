"""
Etapa de EXTRAÇÃO (Extract) do pipeline ETL.

Busca a cotação diária do dólar (PTAX) na API pública do Banco Central
do Brasil. Caso a API esteja indisponível, cai em modo offline com dados
sintéticos no mesmo formato.
"""
from datetime import datetime, timedelta
import random

import pandas as pd
import requests

BASE_URL = (
    "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
    "CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)"
    "?@dataInicial='{data_inicial}'&@dataFinalCotacao='{data_final}'"
    "&$format=json"
)


def extrair_cotacoes(dias: int = 30) -> pd.DataFrame:
    """Extrai as cotações do dólar (PTAX) dos últimos N dias.

    Retorna um DataFrame bruto (etapa Extract).
    """
    hoje = datetime.now()
    data_inicial = (hoje - timedelta(days=dias)).strftime("%m-%d-%Y")
    data_final = hoje.strftime("%m-%d-%Y")

    url = BASE_URL.format(data_inicial=data_inicial, data_final=data_final)

    try:
        resposta = requests.get(url, timeout=10)
        resposta.raise_for_status()
        dados = resposta.json()["value"]
        df = pd.DataFrame(dados)
        df["fonte"] = "api_bcb_ptax"
        print(f"[EXTRACT] {len(df)} registros extraídos da API do Banco Central.")
        return df

    except Exception as e:
        print(f"[EXTRACT] API indisponível ({e}). Gerando dados sintéticos (modo offline).")
        return _gerar_dados_offline(dias)


def _gerar_dados_offline(dias: int = 30) -> pd.DataFrame:
    """Fallback offline: dados sintéticos no mesmo formato da API do BCB."""
    random.seed(42)
    registros = []
    cotacao_base = 5.35
    hoje = datetime.now()

    for i in range(dias):
        data = hoje - timedelta(days=dias - i)
        if data.weekday() >= 5:  # pula fins de semana
            continue
        variacao = random.uniform(-0.04, 0.04)
        cotacao_base = round(max(cotacao_base + variacao, 4.5), 4)
        registros.append({
            "cotacaoCompra": cotacao_base - 0.01,
            "cotacaoVenda": cotacao_base,
            "dataHoraCotacao": data.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "fonte": "dados_sinteticos_offline",
        })

    df = pd.DataFrame(registros)
    print(f"[EXTRACT] {len(df)} registros sintéticos gerados (modo offline).")
    return df
