"""
Etapa de EXTRAÇÃO (Extract) do pipeline ETL.

Busca a cotação diária do dólar (PTAX) na API pública do Banco Central
do Brasil - dados oficiais, gratuitos e sem necessidade de autenticação.

Documentação da API: https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata

Caso a API esteja indisponível ou não haja conexão com a internet,
o script cai automaticamente em modo offline, gerando dados sintéticos
com a mesma estrutura, para que o restante do pipeline continue
demonstrável.
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
import random


BASE_URL = (
    "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
    "CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)"
    "?@dataInicial='{data_inicial}'&@dataFinalCotacao='{data_final}'"
    "&$format=json"
)


def extrair_cotacoes(dias=30):
    """Extrai as cotações do dólar (PTAX) dos últimos N dias.

    Retorna um DataFrame bruto, exatamente como veio da API (sem
    tratamento), representando a etapa de Extract do pipeline.
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
        print(f"[EXTRACT] API indisponível ({e}). Gerando dados sintéticos para demonstração offline.")
        return _gerar_dados_offline(dias)


def _gerar_dados_offline(dias=30):
    """Fallback offline: gera dados no mesmo formato da API do BCB,
    para permitir testar o pipeline sem conexão com a internet."""
    random.seed(42)
    registros = []
    cotacao_base = 5.35
    hoje = datetime.now()

    for i in range(dias):
        data = hoje - timedelta(days=dias - i)
        if data.weekday() >= 5:  # pula fins de semana, como faria o BCB
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


if __name__ == "__main__":
    df_bruto = extrair_cotacoes(dias=30)
    df_bruto.to_csv("dados_brutos_extract.csv", index=False, encoding="utf-8")
    print(f"[EXTRACT] Dados brutos salvos em dados_brutos_extract.csv")
    print(df_bruto.head())
