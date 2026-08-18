"""Testes da etapa de transformação."""

from datetime import datetime, timedelta

import pandas as pd
import pytest

from pipeline_etl.transform import transformar_cotacoes, gerar_agregado_semanal


@pytest.fixture
def df_bruto():
    base = datetime.now()
    return pd.DataFrame([
        {
            "cotacaoCompra": 5.20,
            "cotacaoVenda": 5.21,
            "dataHoraCotacao": (base - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "fonte": "teste",
        },
        {
            "cotacaoCompra": 5.22,
            "cotacaoVenda": 5.23,
            "dataHoraCotacao": (base - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "fonte": "teste",
        },
        {
            "cotacaoCompra": 5.24,
            "cotacaoVenda": 5.25,
            "dataHoraCotacao": base.strftime("%Y-%m-%d %H:%M:%S"),
            "fonte": "teste",
        },
    ])


def test_transformar_cotacoes_colunas(df_bruto):
    resultado = transformar_cotacoes(df_bruto)
    expected = {
        "id", "data", "cotacao_compra", "cotacao_venda", "spread",
        "variacao_pct_dia_anterior", "tendencia", "fonte"
    }
    assert set(resultado.columns) == expected
    assert len(resultado) == 3


def test_spread_calculado(df_bruto):
    resultado = transformar_cotacoes(df_bruto)
    assert resultado.iloc[0]["spread"] == pytest.approx(0.01)


def test_agregado_semanal(df_bruto):
    df_t = transformar_cotacoes(df_bruto)
    agregado = gerar_agregado_semanal(df_t)
    assert "ano_semana" in agregado.columns
    assert "cotacao_media" in agregado.columns
    assert len(agregado) >= 1
