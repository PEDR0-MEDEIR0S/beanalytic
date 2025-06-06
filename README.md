# BeAnalytic - ETL Analítico com Dados da ANATEL

Este projeto realiza o **processamento automatizado, transformação e carga de dados públicos da ANATEL** (serviços SCM, SMP e STFC) em um banco de dados PostgreSQL, estruturado em um modelo dimensional (Data Warehouse). Ele foi desenvolvido para facilitar a análise histórica dos serviços de telecomunicação no Brasil, utilizando boas práticas de ETL e organização modular.

---

## Funcionalidades

- Download automatizado de arquivos `.ods` da ANATEL
- Transformação e normalização dos dados (formato long)
- Carga em tabelas dimensionais e fato no PostgreSQL
- Estrutura de banco com modelo estrela e views analíticas
- Suporte a execução em ambiente local e com Docker
- Modular e totalmente executável via scripts Python

---

## Estrutura do Projeto

```
beanalytic
├── docker-compose.yml
├── dockerfile
├── README.md
│
├── postgres/
│   ├── views.sql             # Views analíticas criadas no banco
│   └── init.sql              # Script SQL inicial de criação de tabelas
│
├── start.sh                  # Script para iniciar o projeto em Linux/Mac
├── requirements.txt          # Dependências Python
│
├── main.py                   # Executa a carga final no banco e aplica views
├── see_data.py               # Faz download e pré-visualização dos dados
├── etl_process.py            # Processa e transforma os arquivos .ods
├── load.py                   # Realiza a carga no banco (dimensões e fato)
├── config.py                 # Cria engine de conexão com o banco
│
├── SCM2019.ods               # Arquivos de dados ANATEL
├── SMP2019.ods
└── STFC2019.ods
```

---

## Modelo de Banco de Dados

O projeto utiliza o PostgreSQL com uma estrutura dimensional (modelo estrela):

### Tabelas Dimensionais

- `dim_empresa` — Nome do grupo econômico
- `dim_variavel` — Indicador/variável observada
- `dim_servico` — Tipo de serviço (SCM, SMP, STFC)
- `dim_tempo` — Data no formato `mes`, `ano`, `mes_num`

### Tabela Fato

- `fato_indicadores` — Fatos numéricos mapeados para IDs das dimensões

### Views

O arquivo `postgres/views.sql` contém views que consolidam dados da fato com as dimensões para análise.

---

## Instalação

### Requisitos

- Python:3.11.12-bookworm
- Postgres:17.5-bookworm
- Docker (opcional)

### Ambiente Linux ou Mac

use o Docker Compose:

```bash
docker compose up --build
```
ou
```bash
chmod +x start.sh
./start.sh
```

### Ambiente Windows

Execute diretamente com Python:

use o Docker Compose:

```bash
docker compose up --build
```
ou
```bash
wsl bash start.sh
python see_data.py
python etl_process.py
python main.py
```



---

## Ordem Recomendada de Execução (History Telling)

1. `see_data.py`  
   Faz o download dos arquivos `.ods` diretamente do site da ANATEL e salva no diretório `~/Desktop/beanalytic`.

2. `etl_process.py`  
   Processa os dados, limpa, transforma e organiza em um DataFrame pronto para carga.

3. `main.py`  
   Conecta ao banco PostgreSQL, carrega as tabelas dimensão e fato e aplica as views.

> Para atualizar os dados futuramente, basta executar novamente o `see_data.py`. Os arquivos são baixados automaticamente para `~/Desktop/beanalytic`.

---

## Variáveis de Ambiente

As conexões são feitas via variáveis de ambiente:

| Variável     | Padrão       |
|--------------|--------------|
| `DB_HOST`    | localhost/db |
| `DB_NAME`    | beanalytic   |
| `DB_USER`    | postgres     |
| `DB_PASS`    | beanalytic   |

Essas variáveis já estão configuradas no `docker-compose.yml`.

---

## Requisitos Python

Instale com:

```bash
pip install -r requirements.txt
```

---

## Licença

Este projeto é livre para uso educacional e científico. Dados públicos da ANATEL sob licença de uso aberto.

---
