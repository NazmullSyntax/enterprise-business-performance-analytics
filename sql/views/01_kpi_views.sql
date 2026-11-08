-- View: monthly factory KPIs
CREATE OR REPLACE VIEW vw_factory_monthly AS
WITH prod AS (
    SELECT f.factory_id, d.year, d.month,
           SUM(p.units_produced)  AS units_produced,
           SUM(p.units_target)    AS units_target,
           SUM(p.defect_units)    AS defect_units,
           SUM(p.downtime_minutes) AS downtime_minutes,
           SUM(p.run_minutes)     AS run_minutes,
           SUM(p.planned_minutes) AS planned_minutes
    FROM fact_production p
    JOIN dim_date d   ON d.date_key = p.date_key
    JOIN dim_factory f ON f.factory_id = p.factory_id
    GROUP BY f.factory_id, d.year, d.month
),
sales AS (
    SELECT f.factory_id, d.year, d.month, SUM(s.revenue) AS revenue
    FROM fact_sales s
    JOIN dim_date d   ON d.date_key = s.date_key
    JOIN dim_factory f ON f.factory_id = s.factory_id
    GROUP BY f.factory_id, d.year, d.month
),
cost AS (
    SELECT factory_id, year, month,
           SUM(raw_material_cost + labor_cost + overhead_cost) AS total_cost,
           SUM(budget_cost) AS budget_cost
    FROM fact_cost
    GROUP BY factory_id, year, month
)
SELECT p.factory_id, p.year, p.month,
       p.units_produced, p.units_target, p.defect_units,
       p.run_minutes, p.planned_minutes,
       ROUND(100.0 * p.units_produced / NULLIF(p.units_target,0), 2)   AS production_achievement_pct,
       ROUND(100.0 * p.defect_units   / NULLIF(p.units_produced,0), 2) AS defect_rate_pct,
       ROUND(100.0 * p.run_minutes    / NULLIF(p.planned_minutes,0), 2) AS utilization_pct,
       ROUND(100.0 * p.downtime_minutes / NULLIF(p.planned_minutes,0), 2) AS downtime_pct,
       COALESCE(s.revenue, 0)     AS revenue,
       COALESCE(c.total_cost, 0)  AS total_cost,
       COALESCE(c.budget_cost, 0) AS budget_cost,
       COALESCE(s.revenue, 0) - COALESCE(c.total_cost, 0) AS profit,
       ROUND(100.0 * (COALESCE(s.revenue,0) - COALESCE(c.total_cost,0))
             / NULLIF(s.revenue,0), 2) AS profit_margin_pct
FROM prod p
LEFT JOIN sales s USING (factory_id, year, month)
LEFT JOIN cost  c USING (factory_id, year, month);