{{ config(alias=env_var("DBT_BQ_VIEW_PRICES_DAILY")) }}

with
    daily_prices as (
        select
            p.item_id as id,
            extract(date from p.recorded_at) as recorded_date,
            min(p.price) as min_price,
            max(p.price) as max_price,
            avg(p.price) as avg_price
        from {{ var("prices_table") }} p
        group by p.item_id, extract(date from p.recorded_at)
    )

select
    i.id,
    i.name,
    i.description,
    cast(d.min_price as int64) as min_price,
    cast(d.max_price as int64) as max_price,
    cast(d.avg_price as int64) as avg_price,
    d.recorded_date
from daily_prices d
inner join {{ var("items_table") }} i on i.id = d.id
