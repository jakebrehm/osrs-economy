{{ config(alias=env_var("DBT_BQ_VIEW_PRICES_WEEKLY")) }}

with
    weekly_prices as (
        select
            p.item_id as id,
            min(p.price) as min_price,
            max(p.price) as max_price,
            avg(p.price) as avg_price
        from {{ var("prices_table") }} p
        where
            extract(date from p.recorded_at) >= date_sub(current_date(), interval 7 day)
        group by p.item_id
    )

select
    i.id,
    i.name,
    i.description,
    cast(w.min_price as int64) as min_price,
    cast(w.max_price as int64) as max_price,
    cast(w.avg_price as int64) as avg_price
from weekly_prices w
inner join {{ var("items_table") }} i on i.id = w.id
