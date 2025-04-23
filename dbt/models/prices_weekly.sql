{{ config(alias=env_var('DBT_BQ_VIEW_PRICES_WEEKLY')) }}

WITH weekly_prices AS (
    SELECT
        p.item_id AS id
        ,MIN(p.price) AS min_price
        ,MAX(p.price) AS max_price
        ,AVG(p.price) AS avg_price
    FROM
        {{ var('prices_table') }} p
    WHERE
        EXTRACT(DATE FROM p.recorded_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
    GROUP BY
        p.item_id
)

SELECT
    i.id
    ,i.name
    ,i.description
    ,CAST(w.min_price AS INT64) AS min_price
    ,CAST(w.max_price AS INT64) AS max_price
    ,CAST(w.avg_price AS INT64) AS avg_price
FROM
    weekly_prices w
INNER JOIN
    {{ var('items_table') }} i
    ON
    i.id = w.id