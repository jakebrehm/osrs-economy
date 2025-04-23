{{ config(alias=env_var('DBT_BQ_VIEW_PRICES_ALL_TIME')) }}

WITH all_time_prices AS (
    SELECT
        p.item_id AS id
        ,MIN(p.price) AS min_price
        ,MAX(p.price) AS max_price
        ,AVG(p.price) AS avg_price
    FROM
        {{ var('prices_table') }} p
    GROUP BY
        p.item_id
)

SELECT
    i.id
    ,i.name
    ,i.description
    ,CAST(a.min_price AS INT64) AS min_price
    ,CAST(a.max_price AS INT64) AS max_price
    ,CAST(a.avg_price AS INT64) AS avg_price
FROM
    all_time_prices a
INNER JOIN
    {{ var('items_table') }} i
    ON
    i.id = a.id