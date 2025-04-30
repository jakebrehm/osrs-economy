{{ config(alias=env_var("DBT_BQ_VIEW_PRICES_LATEST")) }}

with
    ranked_rows as (
        select
            item_id as id,
            price,
            recorded_at,
            row_number() over (
                partition by item_id order by recorded_at desc
            ) as row_num
        from {{ var("prices_table") }}
    )

select i.id, r.price, i.name, i.description, r.recorded_at
from ranked_rows r
inner join {{ var("items_table") }} i on i.id = r.id
where r.row_num = 1
