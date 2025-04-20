{{ config(alias=env_var('DBT_BQ_VIEW_PRICES_DAILY')) }}

WITH daily_prices AS (
    SELECT
        p.item_id AS id
        ,EXTRACT(DATE FROM p.recorded_at) AS recorded_date
        ,MIN(p.price) AS min_price
        ,MAX(p.price) AS max_price
        ,AVG(p.price) AS avg_price
    FROM
        {{ var('prices_table') }} p
    GROUP BY
        p.item_id
        ,EXTRACT(DATE FROM p.recorded_at)
)

SELECT
    i.id
    ,i.name
    ,i.description
    ,CAST(d.min_price AS INT64) AS min_price
    ,CAST(d.max_price AS INT64) AS max_price
    ,CAST(d.avg_price AS INT64) AS avg_price
    ,d.recorded_date
FROM
    daily_prices d
INNER JOIN
    {{ var('items_table') }} i
    ON
    i.id = d.id