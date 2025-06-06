"""
Script principal do processo ETL para carga de dados analíticos no banco PostgreSQL.
Executa a carga do DataFrame final na base e aplica o script de views em SQL, se disponível.
"""

import time
import os
import psycopg2
from psycopg2 import sql
from etl_process import df_final
from load import carregar_no_banco
from config import get_db_engine


time.sleep(10)  # Espera inicial opcional (útil para ambientes com containers que sobem devagar)


def main():
    """
    Executa o processo principal de carga de dados no banco.
    
    Etapas:
    - Geração do engine.
    - Carga das tabelas dimensão e fato via função `carregar_no_banco`.
    """
    print("Iniciando ETL...")
    print(f"Linhas a carregar: {len(df_final)}")

    try:
        engine = get_db_engine()
    except Exception as e:
        print(f"[ERRO] Falha ao obter conexão com o banco: {e}")
        return

    try:
        carregar_no_banco(df_final, engine)
        print("Carga finalizada.")
    except Exception as e:
        print(f"[ERRO] Falha na carga: {e}")


def criar_views():
    """
    Executa o script SQL de criação de views, se o arquivo 'views.sql' existir.

    Arquivo esperado: postgres/views.sql
    """
    time.sleep(10)

    views_path = os.path.join("postgres", "views.sql")

    if not os.path.exists(views_path):
        print("Arquivo de views não localizado. Ignorando etapa.")
        return

    try:
        print("Criando views...")

        conn = psycopg2.connect(
            dbname="beanalytic",
            user="postgres",
            password="beanalytic",
            host="beanalytic-db-1",
            port="5432"
        )
        conn.autocommit = True
        cur = conn.cursor()

        with open(views_path, "r", encoding="utf-8") as f:
            sql_code = f.read()

        cur.execute(sql.SQL(sql_code))

        cur.close()
        conn.close()

        print("Views criadas.")

    except Exception as e:
        print(f"[ERRO] Criação de views falhou: {e}")


if __name__ == "__main__":
    time.sleep(10) 
    main()
    criar_views()
