-- Nexora Manufacturing Ltd. — Star schema
-- All data synthetic. No personal data.

DROP TABLE IF EXISTS fact_inventory, fact_cost, fact_sales, fact_production,
    dim_employee, dim_machine, dim_product, dim_department, dim_factory, dim_date CASCADE;

CREATE TABLE dim_date (
    date_key      INTEGER PRIMARY KEY,
    date          DATE NOT NULL,
    year          INTEGER NOT NULL,
    quarter       VARCHAR(2) NOT NULL,
    month         INTEGER NOT NULL,
    month_name    VARCHAR(10) NOT NULL,
    week          INTEGER NOT NULL,
    day_of_week   VARCHAR(12) NOT NULL,
    is_weekend    BOOLEAN NOT NULL
);

CREATE TABLE dim_factory (
    factory_id            VARCHAR(10) PRIMARY KEY,
    factory_name          VARCHAR(100) NOT NULL,
    region                VARCHAR(50) NOT NULL,
    capacity_units_month  INTEGER NOT NULL
);

CREATE TABLE dim_department (
    department_id  VARCHAR(10) PRIMARY KEY,
    department_name VARCHAR(50) NOT NULL,
    business_unit  VARCHAR(50) NOT NULL
);

CREATE TABLE dim_product (
    product_id     VARCHAR(10) PRIMARY KEY,
    product_name   VARCHAR(100) NOT NULL,
    category       VARCHAR(50) NOT NULL,
    unit_price     NUMERIC(10,2) NOT NULL,
    standard_cost  NUMERIC(10,2) NOT NULL
);

CREATE TABLE dim_machine (
    machine_id    VARCHAR(10) PRIMARY KEY,
    machine_name  VARCHAR(50) NOT NULL,
    factory_id    VARCHAR(10) NOT NULL REFERENCES dim_factory(factory_id),
    machine_type  VARCHAR(30) NOT NULL
);

CREATE TABLE dim_employee (
    employee_code VARCHAR(10) PRIMARY KEY,
    role          VARCHAR(50) NOT NULL,
    department_id VARCHAR(10) NOT NULL REFERENCES dim_department(department_id),
    factory_id    VARCHAR(10) NOT NULL REFERENCES dim_factory(factory_id)
);

CREATE TABLE fact_production (
    date_key          INTEGER NOT NULL REFERENCES dim_date(date_key),
    machine_id        VARCHAR(10) NOT NULL REFERENCES dim_machine(machine_id),
    factory_id        VARCHAR(10) NOT NULL REFERENCES dim_factory(factory_id),
    units_produced    INTEGER NOT NULL,
    units_target      INTEGER NOT NULL,
    downtime_minutes  INTEGER NOT NULL,
    run_minutes       INTEGER NOT NULL,
    planned_minutes   INTEGER NOT NULL,
    defect_units      INTEGER NOT NULL
);

CREATE TABLE fact_sales (
    date_key     INTEGER NOT NULL REFERENCES dim_date(date_key),
    factory_id   VARCHAR(10) NOT NULL REFERENCES dim_factory(factory_id),
    product_id   VARCHAR(10) NOT NULL REFERENCES dim_product(product_id),
    units_sold   INTEGER NOT NULL,
    revenue      NUMERIC(12,2) NOT NULL
);

CREATE TABLE fact_cost (
    year               INTEGER NOT NULL,
    month              INTEGER NOT NULL,
    factory_id         VARCHAR(10) NOT NULL REFERENCES dim_factory(factory_id),
    department_id      VARCHAR(10) NOT NULL REFERENCES dim_department(department_id),
    raw_material_cost  NUMERIC(12,2) NOT NULL,
    labor_cost         NUMERIC(12,2) NOT NULL,
    overhead_cost      NUMERIC(12,2) NOT NULL,
    budget_cost        NUMERIC(12,2) NOT NULL
);

CREATE TABLE fact_inventory (
    year           INTEGER NOT NULL,
    month          INTEGER NOT NULL,
    factory_id     VARCHAR(10) NOT NULL REFERENCES dim_factory(factory_id),
    product_id     VARCHAR(10) NOT NULL REFERENCES dim_product(product_id),
    opening_stock  INTEGER NOT NULL,
    closing_stock  INTEGER NOT NULL,
    stock_value    NUMERIC(12,2) NOT NULL
);

CREATE INDEX idx_prod_date     ON fact_production(date_key);
CREATE INDEX idx_prod_factory  ON fact_production(factory_id);
CREATE INDEX idx_sales_date    ON fact_sales(date_key);
CREATE INDEX idx_sales_factory ON fact_sales(factory_id);
CREATE INDEX idx_cost_factory  ON fact_cost(factory_id, year, month);