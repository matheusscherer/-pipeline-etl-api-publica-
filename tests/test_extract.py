"""Testes da etapa de extração (modo offline)."""

from pipeline_etl.extract import _gerar_dados_offline


def test_gerar_dados_offline_retorna_dataframe():
    df = _gerar_dados_offline(dias=10)
    assert len(df) > 0
    assert "cotacaoCompra" in df.columns
    assert "cotacaoVenda" in df.columns
    assert "dataHoraCotacao" in df.columns
    assert (df["fonte"] == "dados_sinteticos_offline").all()
