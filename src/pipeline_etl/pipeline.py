"""
Orquestrador do Pipeline ETL - Cotação do Dólar (PTAX/Banco Central).

Extract → Transform → Load
"""
import sqlite3
import time

from pipeline_etl.extract import extrair_cotacoes
from pipeline_etl.transform import transformar_cotacoes, gerar_agregado_semanal
from pipeline_etl.load import carregar_no_banco


def rodar_pipeline(dias: int = 30) -> str:
    inicio = time.time()
    print("=" * 60)
    print("PIPELINE ETL - COTAÇÃO DO DÓLAR (BANCO CENTRAL)")
    print("=" * 60)

    print("\n--- ETAPA 1: EXTRACT ---")
    df_bruto = extrair_cotacoes(dias=dias)

    print("\n--- ETAPA 2: TRANSFORM ---")
    df_transformado = transformar_cotacoes(df_bruto)
    df_semanal = gerar_agregado_semanal(df_transformado)
    print(f"[TRANSFORM] {len(df_transformado)} registros diários, {len(df_semanal)} semanas agregadas.")

    print("\n--- ETAPA 3: LOAD ---")
    caminho_db = carregar_no_banco(df_transformado, df_semanal)

    duracao = time.time() - inicio
    print(f"\nPipeline concluído em {duracao:.2f}s")

    print("\n--- VALIDAÇÃO FINAL: consultando o banco ---")
    conn = sqlite3.connect(caminho_db)
    resultado = conn.execute("""
        SELECT data, cotacao_venda, tendencia
        FROM fato_cotacao_diaria
        ORDER BY data DESC
        LIMIT 5
    """).fetchall()
    conn.close()

    print("Últimas 5 cotações carregadas:")
    for linha in resultado:
        print(f"  {linha[0]} | R$ {linha[1]:.4f} | {linha[2]}")

    return caminho_db


def main() -> None:
    rodar_pipeline(dias=30)


if __name__ == "__main__":
    main()
