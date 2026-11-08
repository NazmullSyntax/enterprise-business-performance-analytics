-- Month-over-month revenue growth using LAG
WITH monthly AS (
    SELECT year, month, SUM(revenue) AS revenue
    FROM vw_factory_monthly
    GROUP BY year, month
)
SELECT year, month, revenue,
       LAG(revenue) OVER (ORDER BY year, month) AS prev_revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY year, month))
             / NULLIF(LAG(revenue) OVER (ORDER BY year, month), 0), 2) AS mom_growth_pct
FROM monthly
ORDER BY year, month;