# Database Design — Nexora Analytics

All data synthetic. Employees identified by `employee_code` only — no PII.

```mermaid
erDiagram
    dim_date       ||--o{ fact_production : date_key
    dim_date       ||--o{ fact_sales      : date_key
    dim_factory    ||--o{ fact_production : factory_id
    dim_factory    ||--o{ fact_sales      : factory_id
    dim_factory    ||--o{ fact_cost       : factory_id
    dim_factory    ||--o{ fact_inventory  : factory_id
    dim_factory    ||--o{ dim_machine     : factory_id
    dim_factory    ||--o{ dim_employee    : factory_id
    dim_department ||--o{ fact_cost       : department_id
    dim_department ||--o{ dim_employee    : department_id
    dim_product    ||--o{ fact_sales      : product_id
    dim_product    ||--o{ fact_inventory  : product_id
    dim_machine    ||--o{ fact_production : machine_id
```

**Grain summary**
- `fact_production`: one machine × one day
- `fact_sales`: one product × one factory × one day
- `fact_cost`: one factory × one department × one month
- `fact_inventory`: one product × one factory × one month