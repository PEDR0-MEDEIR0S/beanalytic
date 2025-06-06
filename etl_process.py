"""
Script para processamento de arquivos .ods contendo dados mensais (SCM, SMP, STFC).
Realiza leitura, limpeza, transformação de dados para formato long e unificação em um único DataFrame.
"""

import pandas as pd
from pathlib import Path
import re

# Diretório de origem dos arquivos
desktop = Path.home() / "Desktop"
move = desktop / "beanalytic"

# Lista de arquivos a serem processados
arquivos = ["SCM2019.ods", "SMP2019.ods", "STFC2019.ods"]

def processar_arquivo(path_arquivo):
    """
    Lê, limpa e transforma os dados de um arquivo ODS.

    Args:
        path_arquivo (Path): Caminho completo do arquivo a ser processado.

    Returns:
        pd.DataFrame | None: DataFrame transformado no formato long ou None em caso de erro.
    """
    print(f"-> {path_arquivo.name}")

    try:
        df = pd.read_excel(path_arquivo, engine="odf", skiprows=8, dtype=str)
    except Exception as e:
        print(f"[ERRO] Leitura falhou: {e}")
        return None

    try:
        df.dropna(axis=1, how="all", inplace=True)
        df.columns = [str(col).strip().replace("\n", " ") for col in df.columns]

        colunas_id = df.columns[:2]
        colunas_valores = [
            col for col in df.columns[2:]
            if str(col).strip().lower().startswith((
                'jan', 'fev', 'mar', 'abr', 'mai', 'jun',
                'jul', 'ago', 'set', 'out', 'nov', 'dez'
            )) or "-" in str(col)
        ]

        df.dropna(subset=colunas_valores, how="all", inplace=True)

        df_long = pd.melt(
            df,
            id_vars=colunas_id,
            value_vars=colunas_valores,
            var_name="Mes",
            value_name="Valor",
        )

        df_long["Valor"] = pd.to_numeric(df_long["Valor"], errors='coerce').round(3).astype(str)

        df_long["Mes"] = (
            df_long["Mes"]
            .astype(str)
            .str.replace("/", "-", regex=False)
            .str.extract(r"(\d{4})[-/]?(\d{2})")
            .apply(lambda x: f"{x[0]}-{x[1]}", axis=1)
        )

        return df_long

    except Exception as e:
        print(f"[ERRO] Processamento falhou: {e}")
        return None


# Mapeamento para adicionar coluna identificadora
column_df = {
    "SCM2019.ods": "SCM",
    "SMP2019.ods": "SMP",
    "STFC2019.ods": "STFC"
}

union_df = []

# Processa os arquivos existentes
for nome_arquivo in arquivos:
    caminho = move / nome_arquivo
    if not caminho.exists():
        print(f"[AVISO] Arquivo ausente: {caminho.name}")
        continue

    df = processar_arquivo(caminho)
    if df is not None:
        df["IDA"] = column_df[nome_arquivo]
        union_df.append(df)

# Verifica se houve dados a consolidar
if not union_df:
    print("[FIM] Nenhum dado processado.")
else:
    try:
        df_final = pd.concat(union_df, ignore_index=True)

        print("\n[OK] DataFrame consolidado:")
        print(df_final.head(5))
        print(df_final.tail(5))
        print(df_final.describe())
    except Exception as e:
        print(f"[ERRO] Falha ao concatenar DataFrames: {e}")
