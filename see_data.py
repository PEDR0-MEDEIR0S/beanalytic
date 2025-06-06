"""
Script: see_data.py

Descrição:
Este script automatiza o processo de download e leitura de arquivos de dados abertos 
disponibilizados pela ANATEL (Agência Nacional de Telecomunicações). 
Os arquivos referem-se aos serviços SCM, SMP e STFC do ano de 2019 e são salvos no diretório 
"beanalytic" na área de trabalho do usuário. Após o download, os dados são carregados com pandas 
para pré-visualização.

Dependências:
- requests
- pandas
- pathlib
"""

import os
import requests
import pandas as pd
from pathlib import Path
from requests.exceptions import (
    ConnectionError,
    Timeout,
    RequestException,
    HTTPError,
)

# Mapeamento dos arquivos a serem baixados com suas respectivas URLs
files_to_download = {
    "SCM2019.ods": "http://anatel.gov.br/dadosabertos/PDA/IDA/SCM2019.ods",
    "SMP2019.ods": "http://anatel.gov.br/dadosabertos/PDA/IDA/SMP2019.ods",
    "STFC2019.ods": "http://anatel.gov.br/dadosabertos/PDA/IDA/STFC2019.ods",
}

# Define o caminho para salvar os arquivos baixados
desktop_path = Path.home() / "Desktop"
destination_path = desktop_path / "beanalytic"
destination_path.mkdir(parents=True, exist_ok=True)


def download_file(file_name: str, file_url: str) -> Path | None:
    """
    Faz o download de um arquivo da web e o salva localmente.

    Args:
        file_name (str): Nome do arquivo que será salvo.
        file_url (str): URL de onde o arquivo será baixado.

    Returns:
        Path | None: Caminho para o arquivo salvo ou None se falhar.
    """
    target_path = destination_path / file_name
    print(f"\nIniciando download de '{file_name}' a partir de {file_url}...")

    try:
        response = requests.get(file_url, timeout=30)
        response.raise_for_status()

        if 'html' in response.headers.get('Content-Type', '').lower():
            raise ValueError("Tipo de arquivo não esperado")

        with open(target_path, "wb") as output_file:
            output_file.write(response.content)

        print(f"Download salvo em '{target_path}'")
        return target_path

    except ConnectionError:
        print(f"Erro: erro de conexão '{file_name}'")
    except Timeout:
        print(f"Erro: tempo limite excedido ao tentar baixar '{file_name}'.")
    except HTTPError as http_err:
        print(f"Erro HTTP ao baixar '{file_name}': {http_err}")
    except ValueError as val_err:
        print(f"Erro de conteúdo para '{file_name}': {val_err}")
    except RequestException as req_err:
        print(f"Erro de requisição ao baixar '{file_name}': {req_err}")
    except Exception as err:
        print(f"Erro inesperado ao baixar '{file_name}': {err}")

    return None


# Loop principal: faz download e leitura dos arquivos
for file_name, file_url in files_to_download.items():
    downloaded_path = download_file(file_name, file_url)

    if downloaded_path and downloaded_path.exists():
        print(f"\nProcessando o conteúdo de '{file_name}'...")

        try:
            df = pd.read_excel(downloaded_path, engine="odf", skiprows=8)
            print(f"Pré-visualização dos dados de '{file_name}':\n{df.head()}\n")

        except FileNotFoundError:
            print(f"Erro: o arquivo '{file_name}' caminho não encontrado.")
        except ValueError as val_err:
            print(f"Erro ao ler '{file_name}': {val_err}")
        except Exception as err:
            print(f"Erro ao carregar '{file_name}': {err}")
    else:
        print(f"Falha: o arquivo '{file_name}' erro no download.")

print("\nProcessamento concluído.")
