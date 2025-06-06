-- Criação das views analíticas
-- Apresenta a variação mensal da taxa de resposta em 5 dias úteis por grupo econômico,
-- com média geral e diferença da média por grupo.

SELECT 'Criando view vw_variacao_ida' AS status;

DROP VIEW IF EXISTS vw_variacao_ida;

DO $$
DECLARE
    colunas_dinamicas TEXT;
    sql TEXT;
BEGIN
    SELECT string_agg(
        format(
            'ROUND(AVG(CASE WHEN grupo_economico = %L THEN diferenca END)::numeric, 4) AS %I',
            grupo_economico,
            grupo_economico
        ),
        ', '
    ) INTO colunas_dinamicas
    FROM (
        SELECT DISTINCT de.nome AS grupo_economico
        FROM fato_indicadores fi
        JOIN dim_empresa de ON de.id_empresa = fi.id_empresa
    ) sub;

    sql := format($f$
        CREATE OR REPLACE VIEW vw_variacao_ida AS
        WITH base AS (
            SELECT
                dt.mes,
                de.nome AS grupo_economico,
                fi.valor / 100.0 AS valor,
                LAG(fi.valor / 100.0) OVER (PARTITION BY de.nome ORDER BY dt.mes) AS valor_anterior
            FROM fato_indicadores fi
            JOIN dim_variavel dv ON dv.id_variavel = fi.id_variavel
            JOIN dim_empresa de ON de.id_empresa = fi.id_empresa
            JOIN dim_tempo dt ON dt.id_tempo = fi.id_tempo
            WHERE dv.nome_variavel = 'Taxa de Respondidas em 5 dias Úteis'
        ),
        variacoes AS (
            SELECT
                mes,
                grupo_economico,
                ROUND(((valor - valor_anterior) / NULLIF(valor_anterior, 0))::numeric, 4) AS variacao
            FROM base
            WHERE valor_anterior IS NOT NULL
        ),
        media_por_mes AS (
            SELECT
                mes,
                ROUND(AVG(variacao)::numeric, 4) AS media
            FROM variacoes
            GROUP BY mes
        ),
        pivot AS (
            SELECT
                v.mes,
                v.grupo_economico,
                v.variacao,
                m.media,
                ROUND(v.variacao - m.media, 4) AS diferenca
            FROM variacoes v
            JOIN media_por_mes m ON v.mes = m.mes
        )
        SELECT
            mes,
            ROUND(AVG(variacao * 100)::numeric, 4) AS taxa_de_variacao,
            ROUND(AVG(media)::numeric, 4) AS media,
            %s
        FROM pivot
        GROUP BY mes
        ORDER BY mes;

        COMMENT ON VIEW vw_variacao_ida IS 'Variação mensal da Taxa de Respondidas em 5 dias Úteis por grupo econômico, com média e diferença';
    $f$, colunas_dinamicas);

    EXECUTE sql;
END $$;
