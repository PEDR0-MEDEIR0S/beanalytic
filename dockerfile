# Dockerfile
# Imagem para executar o ETL Python com base no Python 3.11
# Instala dependências e executa o script principal main.py no diretório /app

FROM python:3.11.12-bookworm

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Executa o script main.py
CMD ["python", "main.py"]
