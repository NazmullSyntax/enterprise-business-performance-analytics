"""
Nexora Manufacturing Ltd. — Synthetic Data Generator
=====================================================
Generates fictional data for the Enterprise Business Performance
Analytics project.

ALL DATA IS SYNTHETIC. No real company, employee, or business data.
Employees are identified by code only (EMP-0001); no names, emails,
phones, or salaries.

Generates (into data/raw/):
  Dimensions : dim_date, dim_factory, dim_department, dim_product,
               dim_machine, dim_employee
  Facts      : fact_production, fact_sales, fact_cost, fact_inventory
               (with deliberately planted quality issues for Day 2)

Run (from project root):
    python data/synthetic_data_generator.py
"""

import os
import random
from datetime import date, timedelta

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

RAW_DIR = os.path.join(os.path.dirname(__file__), "raw")
os.makedirs(RAW_DIR, exist_ok=True)

START_DATE = date(2024, 1, 1)
END_DATE = date(2024, 12, 31)


def save(df: pd.DataFrame, name: str) -> None:
    path = os.path.join(RAW_DIR, name)
    df.to_csv(path, index=False)
    print(f"  saved {name:30s} rows={len(df):>6d}")


# ----------------------------------------------------------------------
# DIMENSIONS
# ----------------------------------------------------------------------
def build_dim_date() -> pd.DataFrame:
    rows = []
    d = START_DATE
    while d <= END_DATE:
        rows.append({
            "date_key": int(d.strftime("%Y%m%d")),
            "date": d.isoformat(),
            "year": d.year,
            "quarter": f"Q{(d.month - 1) // 3 + 1}",
            "month": d.month,
            "month_name": d.strftime("%b"),
            "week": d.isocalendar().week,
            "day_of_week": d.strftime("%A"),
            "is_weekend": d.weekday() >= 5,
        })
        d += timedelta(days=1)
    return pd.DataFrame(rows)


def build_dim_factory() -> pd.DataFrame:
    factories = [
        ("F01", "Northfield Plant",   "North Region", 120_000),
        ("F02", "Riverside Works",    "East Region",   95_000),
        ("F03", "Summit Industrial",  "South Region", 110_000),
        ("F04", "Harbor Point Plant", "West Region",   80_000),
    ]
    return pd.DataFrame(factories, columns=[
        "factory_id", "factory_name", "region", "capacity_units_month"
    ])


def build_dim_department() -> pd.DataFrame:
    departments = [
        ("D01", "Production",  "Manufacturing BU"),
        ("D02", "Quality",     "Manufacturing BU"),
        ("D03", "Maintenance", "Manufacturing BU"),
        ("D04", "Sales",       "Commercial BU"),
        ("D05", "Finance",     "Corporate BU"),
        ("D06", "Logistics",   "Commercial BU"),
    ]
    return pd.DataFrame(departments, columns=[
        "department_id", "department_name", "business_unit"
    ])


def build_dim_product() -> pd.DataFrame:
    products = [
        ("P01", "Alpha Valve",    "Components",  85.00,  58.00),
        ("P02", "Beta Bracket",   "Components",  42.50,  27.00),
        ("P03", "Gamma Assembly", "Assemblies", 210.00, 148.00),
        ("P04", "Delta Coupling", "Components",  66.00,  41.00),
        ("P05", "Omega Module",   "Assemblies", 340.00, 235.00),
        ("P06", "Sigma Fastener", "Hardware",    12.00,   6.50),
        ("P07", "Tau Bearing",    "Hardware",    28.00,  15.00),
        ("P08", "Zeta Housing",   "Assemblies", 175.00, 120.00),
    ]
    return pd.DataFrame(products, columns=[
        "product_id", "product_name", "category", "unit_price", "standard_cost"
    ])


def build_dim_machine(factories: pd.DataFrame) -> pd.DataFrame:
    machine_types = ["CNC", "Press", "Assembly", "Packaging"]
    rows, mid = [], 1
    for fid in factories["factory_id"]:
        for i in range(4):
            rows.append({
                "machine_id": f"M{mid:03d}",
                "machine_name": f"{machine_types[i]}-{fid}",
                "factory_id": fid,
                "machine_type": machine_types[i],
            })
            mid += 1
    return pd.DataFrame(rows)


def build_dim_employee(factories: pd.DataFrame, departments: pd.DataFrame,
                       per_dept: int = 5) -> pd.DataFrame:
    roles = {
        "D01": "Operator", "D02": "Quality Inspector",
        "D03": "Technician", "D04": "Sales Analyst",
        "D05": "Finance Analyst", "D06": "Logistics Officer",
    }
    rows, eid = [], 1
    for fid in factories["factory_id"]:
        for did in departments["department_id"]:
            for _ in range(per_dept):
                rows.append({
                    "employee_code": f"EMP-{eid:04d}",
                    "role": roles[did],
                    "department_id": did,
                    "factory_id": fid,
                })
                eid += 1
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------
# FACT TABLES  (with deliberately planted quality issues for Day 2)
# ----------------------------------------------------------------------
def build_fact_production(dim_date, dim_factory, dim_machine) -> pd.DataFrame:
    rows = []
    # factory-level base efficiency so rankings later are meaningful
    base_eff = {"F01": 0.97, "F02": 0.88, "F03": 0.93, "F04": 0.82}

    for _, d in dim_date.iterrows():
        if d["is_weekend"]:
            continue
        for _, m in dim_machine.iterrows():
            fid = m["factory_id"]
            planned = 480  # minutes per shift
            eff = np.random.normal(base_eff[fid], 0.03)
            eff = min(max(eff, 0.60), 1.00)
            run = int(planned * eff)
            downtime = planned - run
            target = int(np.random.normal(500, 40))
            produced = int(target * eff * np.random.uniform(0.95, 1.05))
            defect = int(produced * np.random.uniform(0.005, 0.03))
            rows.append({
                "date_key": d["date_key"],
                "machine_id": m["machine_id"],
                "factory_id": fid,
                "units_produced": produced,
                "units_target": target,
                "downtime_minutes": downtime,
                "run_minutes": run,
                "planned_minutes": planned,
                "defect_units": defect,
            })
    df = pd.DataFrame(rows)

    # ---------- planted quality issues (ON PURPOSE) ----------
    # 1) ~1% duplicate rows
    dup = df.sample(frac=0.01, random_state=1)
    df = pd.concat([df, dup], ignore_index=True)

    # 2) a few negative defect counts
    idx = df.sample(5, random_state=2).index
    df.loc[idx, "defect_units"] = -1

    # 3) some null downtime
    idx = df.sample(8, random_state=3).index
    df.loc[idx, "downtime_minutes"] = np.nan

    # 4) inconsistent factory casing
    df["factory_id"] = df["factory_id"].astype(str)
    idx = df.sample(10, random_state=4).index
    df.loc[idx, "factory_id"] = df.loc[idx, "factory_id"].str.lower()

    # 5) two orphan machine IDs (not present in dim_machine)
    idx = df.sample(2, random_state=5).index
    df.loc[idx, "machine_id"] = "M999"

    return df


def build_fact_sales(dim_date, dim_factory, dim_product) -> pd.DataFrame:
    rows = []
    for _, d in dim_date.iterrows():
        for _, f in dim_factory.iterrows():
            for _, p in dim_product.iterrows():
                if np.random.rand() < 0.55:  # not every product sells daily
                    continue
                qty = int(np.random.gamma(2.0, 15))
                rows.append({
                    "date_key": d["date_key"],
                    "factory_id": f["factory_id"],
                    "product_id": p["product_id"],
                    "units_sold": qty,
                    "revenue": round(qty * p["unit_price"], 2),
                })
    df = pd.DataFrame(rows)

    # planted issue: 3 rows with negative revenue
    idx = df.sample(3, random_state=6).index
    df.loc[idx, "revenue"] = -100.0

    return df


def build_fact_cost(dim_date, dim_factory, dim_department) -> pd.DataFrame:
    rows = []
    months = dim_date.drop_duplicates("month")[["year", "month"]]
    for _, mm in months.iterrows():
        for _, f in dim_factory.iterrows():
            for _, dpt in dim_department.iterrows():
                raw = round(np.random.uniform(180_000, 320_000), 2)
                labor = round(np.random.uniform(90_000, 150_000), 2)
                overhead = round(np.random.uniform(40_000, 80_000), 2)
                budget = round((raw + labor + overhead) *
                               np.random.uniform(0.9, 1.1), 2)
                rows.append({
                    "year": mm["year"],
                    "month": mm["month"],
                    "factory_id": f["factory_id"],
                    "department_id": dpt["department_id"],
                    "raw_material_cost": raw,
                    "labor_cost": labor,
                    "overhead_cost": overhead,
                    "budget_cost": budget,
                })
    return pd.DataFrame(rows)


def build_fact_inventory(dim_date, dim_factory, dim_product) -> pd.DataFrame:
    rows = []
    months = dim_date.drop_duplicates("month")[["year", "month"]]
    for _, mm in months.iterrows():
        for _, f in dim_factory.iterrows():
            for _, p in dim_product.iterrows():
                opening = int(np.random.uniform(200, 1500))
                closing = int(np.random.uniform(200, 1500))
                value = round(closing * p["standard_cost"], 2)
                rows.append({
                    "year": mm["year"],
                    "month": mm["month"],
                    "factory_id": f["factory_id"],
                    "product_id": p["product_id"],
                    "opening_stock": opening,
                    "closing_stock": closing,
                    "stock_value": value,
                })
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------
# main
# ----------------------------------------------------------------------
def main() -> None:
    print("Generating synthetic dimension tables (Nexora Manufacturing Ltd.)...")
    dim_date = build_dim_date()
    dim_factory = build_dim_factory()
    dim_department = build_dim_department()
    dim_product = build_dim_product()
    dim_machine = build_dim_machine(dim_factory)
    dim_employee = build_dim_employee(dim_factory, dim_department)

    save(dim_date, "dim_date.csv")
    save(dim_factory, "dim_factory.csv")
    save(dim_department, "dim_department.csv")
    save(dim_product, "dim_product.csv")
    save(dim_machine, "dim_machine.csv")
    save(dim_employee, "dim_employee.csv")

    print("\nGenerating synthetic fact tables...")
    fact_production = build_fact_production(dim_date, dim_factory, dim_machine)
    fact_sales = build_fact_sales(dim_date, dim_factory, dim_product)
    fact_cost = build_fact_cost(dim_date, dim_factory, dim_department)
    fact_inventory = build_fact_inventory(dim_date, dim_factory, dim_product)

    save(fact_production, "fact_production.csv")
    save(fact_sales, "fact_sales.csv")
    save(fact_cost, "fact_cost.csv")
    save(fact_inventory, "fact_inventory.csv")

    print("\nAll synthetic tables generated.")


if __name__ == "__main__":
    main()