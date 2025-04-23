{{ config(alias=env_var("DBT_BQ_VIEW_PRICES_ALL_TIME")) }}

with
    all_time_prices as (
        select
            p.item_id as id,
            min(p.price) as min_price,
            max(p.price) as max_price,
            avg(p.price) as avg_price
        from {{ var("prices_table") }} p
        group by p.item_id
    )

select
    i.id,
    i.name,
    i.description,
    cast(a.min_price as int64) as min_price,
    cast(a.max_price as int64) as max_price,
    cast(a.avg_price as int64) as avg_price
from all_time_prices a
inner join {{ var("items_table") }} i on i.id = a.id
