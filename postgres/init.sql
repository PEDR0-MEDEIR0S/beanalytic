-- Script de criação das tabelas de dimensões e tabela fato do modelo analítico.
-- Define estrutura relacional para indicadores mensais de serviços e empresas reguladas.

CREATE TABLE IF NOT EXISTS dim_tempo (
    id_tempo SERIAL PRIMARY KEY,
    mes DATE UNIQUE,
    ano INT,
    mes_num INT
);
COMMENT ON TABLE dim_tempo IS 'Dimensão de tempo no formato ano-mês';
COMMENT ON COLUMN dim_tempo.mes IS 'Data representando o primeiro dia do mês (YYYY-MM-01)';
COMMENT ON COLUMN dim_tempo.ano IS 'Ano correspondente ao campo mes';
COMMENT ON COLUMN dim_tempo.mes_num IS 'Número do mês (1 a 12)';

CREATE TABLE IF NOT EXISTS dim_servico (
    id_servico SERIAL PRIMARY KEY,
    sigla VARCHAR(10) UNIQUE
);
COMMENT ON TABLE dim_servico IS 'Dimensão dos serviços monitorados (ex: SCM, SMP)';
COMMENT ON COLUMN dim_servico.sigla IS 'Sigla do serviço';

CREATE TABLE IF NOT EXISTS dim_empresa (
    id_empresa SERIAL PRIMARY KEY,
    nome VARCHAR(100) UNIQUE
);
COMMENT ON TABLE dim_empresa IS 'Dimensão de grupos econômicos';
COMMENT ON COLUMN dim_empresa.nome IS 'Nome do grupo econômico';

CREATE TABLE IF NOT EXISTS dim_variavel (
    id_variavel SERIAL PRIMARY KEY,
    nome_variavel TEXT UNIQUE
);
COMMENT ON TABLE dim_variavel IS 'Dimensão das variáveis monitoradas';
COMMENT ON COLUMN dim_variavel.nome_variavel IS 'Descrição da variável (indicador)';

CREATE TABLE IF NOT EXISTS fato_indicadores (
    id_fato SERIAL PRIMARY KEY,
    id_tempo INT NOT NULL REFERENCES dim_tempo(id_tempo),
    id_empresa INT NOT NULL REFERENCES dim_empresa(id_empresa),
    id_variavel INT NOT NULL REFERENCES dim_variavel(id_variavel),
    id_servico INT NOT NULL REFERENCES dim_servico(id_servico),
    valor FLOAT NOT NULL
);
COMMENT ON TABLE fato_indicadores IS 'Tabela fato com os valores mensais dos indicadores';
COMMENT ON COLUMN fato_indicadores.valor IS 'Valor numérico associado ao indicador';

