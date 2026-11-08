-- Budget vs actual with variance and status
SELECT factory_id, year, month,
       total_cost, budget_cost,
       total_cost - budget_cost AS variance,
       ROUND(100.0 * (total_cost - budget_cost) / NULLIF(budget_cost,0), 2) AS variance_pct,
       CASE
         WHEN total_cost <= budget_cost            THEN 'GREEN'
         WHEN total_cost <= budget_cost * 1.05     THEN 'AMBER'
         ELSE 'RED'
       END AS status
FROM vw_factory_monthly
ORDER BY year, month, factory_id;