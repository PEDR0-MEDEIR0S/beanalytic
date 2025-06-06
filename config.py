"""
Módulo de configuração de acesso ao banco de dados PostgreSQL.
Responsável por construir e retornar um SQLAlchemy Engine com base nas variáveis de ambiente.
"""

import os
from sqlalchemy import create_engine


def get_db_engine():
    """
    Cria e retorna uma engine de conexão com o banco PostgreSQL.

    Parâmetros de conexão são lidos das seguintes variáveis de ambiente:
    - DB_USER (default: postgres)
    - DB_PASS (default: beanalytic)
    - DB_HOST (default: localhost)
    - DB_NAME (default: beanalytic)
    - DB_PORT (default: 5432)

    Returns:
        sqlalchemy.engine.Engine: Instância de engine conectável.

    Raises:
        Exception: Caso ocorra erro ao criar a engine.
    """
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASS", "beanalytic")
    host = os.getenv("DB_HOST", "localhost")
    db = os.getenv("DB_NAME", "beanalytic")
    port = 5432

    url = f"postgresql://{user}:{password}@{host}:{port}/{db}"

    try:
        engine = create_engine(url)
        print(f"Engine criada para {host}:{port}/{db}")
        return engine
    except Exception as e:
        print(f"[ERRO] Falha ao criar engine: {e}")
        raise
