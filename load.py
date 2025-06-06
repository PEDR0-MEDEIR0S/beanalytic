"""
Script de carga de dados no banco relacional via SQLAlchemy.
Realiza o carregamento das tabelas de dimensão (empresa, variável, serviço, tempo)
e posteriormente popula a tabela fato com os dados normalizados.
"""

import pandas as pd
from sqlalchemy import text


def carregar_dimensoes(df: pd.DataFrame, engine) -> None:
    """
    Carrega os dados das tabelas de dimensão no banco: empresa, variável, serviço e tempo.

    Args:
        df (pd.DataFrame): DataFrame contendo os dados brutos já transformados.
        engine: Conexão SQLAlchemy com o banco de dados.

    Returns:
        None
    """
    try:
        empresas = df[['GRUPO ECONÔMICO']].drop_duplicates().rename(columns={'GRUPO ECONÔMICO': 'nome'})
        empresas.to_sql('dim_empresa', engine, if_exists='append', index=False)
        print("dim_empresa -> OK")
    except Exception as e:
        print(f"[ERRO] dim_empresa: {e}")

    try:
        variaveis = df[['VARIÁVEL']].drop_duplicates().rename(columns={'VARIÁVEL': 'nome_variavel'})
        variaveis.to_sql('dim_variavel', engine, if_exists='append', index=False)
        print("dim_variavel -> OK")
    except Exception as e:
        print(f"[ERRO] dim_variavel: {e}")

    try:
        servicos = df[['IDA']].drop_duplicates().rename(columns={'IDA': 'sigla'})
        servicos.to_sql('dim_servico', engine, if_exists='append', index=False)
        print("dim_servico -> OK")
    except Exception as e:
        print(f"[ERRO] dim_servico: {e}")

    try:
        df['mes'] = pd.to_datetime(df['Mes'] + '-01')
        df['ano'] = df['mes'].dt.year
        df['mes_num'] = df['mes'].dt.month
        tempo = df[['mes', 'ano', 'mes_num']].drop_duplicates()
        tempo.to_sql('dim_tempo', engine, if_exists='append', index=False, method='multi')
        print("dim_tempo -> OK")
    except Exception as e:
        print(f"[ERRO] dim_tempo: {e}")


def get_dim_id_map(engine, table_name: str, key_column: str, id_column: str = None) -> dict:
    """
    Retorna um dicionário de mapeamento entre a chave de negócio e o ID da dimensão.

    Args:
        engine: Conexão SQLAlchemy com o banco de dados.
        table_name (str): Nome da tabela de dimensão.
        key_column (str): Coluna usada como chave de negócio.
        id_column (str, optional): Nome da coluna ID. Caso não informado, assume padrão 'id_<tabela>'.

    Returns:
        dict: Mapeamento {chave: id}
    """
    id_column = id_column or f'id_{table_name.replace("dim_", "")}'
    query = f"SELECT {id_column}, {key_column} FROM {table_name}"
    try:
        df = pd.read_sql(query, engine)
        return dict(zip(df[key_column], df[id_column]))
    except Exception as e:
        print(f"[ERRO] Mapeamento {table_name}: {e}")
        return {}


def carregar_fato(df: pd.DataFrame, engine) -> None:
    """
    Carrega os dados na tabela fato, mapeando os valores das dimensões para seus respectivos IDs.

    Args:
        df (pd.DataFrame): DataFrame contendo os dados brutos já transformados.
        engine: Conexão SQLAlchemy com o banco de dados.

    Returns:
        None
    """
    try:
        empresa_map = get_dim_id_map(engine, 'dim_empresa', 'nome')
        variavel_map = get_dim_id_map(engine, 'dim_variavel', 'nome_variavel')
        servico_map = get_dim_id_map(engine, 'dim_servico', 'sigla')
        tempo_map = get_dim_id_map(engine, 'dim_tempo', 'mes', 'id_tempo')

        df['mes'] = pd.to_datetime(df['Mes'] + '-01')

        df_fato = pd.DataFrame({
            'id_empresa': df['GRUPO ECONÔMICO'].map(empresa_map),
            'id_variavel': df['VARIÁVEL'].map(variavel_map),
            'id_servico': df['IDA'].map(servico_map),
            'id_tempo': df['mes'].map(tempo_map),
            'valor': pd.to_numeric(df['Valor'], errors='coerce')
        })

        df_fato.dropna(inplace=True)
        df_fato.to_sql('fato_indicadores', engine, if_exists='replace', index=False)
        print("fato_indicadores -> OK")

    except Exception as e:
        print(f"[ERRO] fato_indicadores: {e}")


def carregar_no_banco(df: pd.DataFrame, engine) -> None:
    """
    Orquestra o processo de carga dos dados nas tabelas dimensionais e fato.

    Args:
        df (pd.DataFrame): DataFrame com os dados já prontos para carga.
        engine: Conexão SQLAlchemy com o banco de dados.

    Returns:
        None
    """
    print("Iniciando carga...")

    try:
        carregar_dimensoes(df, engine)
    except Exception as e:
        print(f"[ERRO] Etapa dimensões: {e}")

    try:
        carregar_fato(df, engine)
    except Exception as e:
        print(f"[ERRO] Etapa fato: {e}")

    print("Carga concluída.")
