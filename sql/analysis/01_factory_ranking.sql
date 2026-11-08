-- Rank factories by total profit using window function
WITH factory_totals AS (
    SELECT factory_id,
           SUM(revenue)    AS total_revenue,
           SUM(total_cost) AS total_cost,
           SUM(profit)     AS total_profit
    FROM vw_factory_monthly
    GROUP BY factory_id
)
SELECT f.factory_name,
       t.total_revenue, t.total_cost, t.total_profit,
       RANK() OVER (ORDER BY t.total_profit DESC) AS profit_rank
FROM factory_totals t
JOIN dim_factory f USING (factory_id)
ORDER BY profit_rank;