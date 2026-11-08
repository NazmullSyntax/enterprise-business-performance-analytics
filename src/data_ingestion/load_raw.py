"""Read all raw CSVs into a dict of DataFrames."""
import os
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")

def load_all() -> dict:
    files = [
        "dim_date", "dim_factory", "dim_department", "dim_product",
        "dim_machine", "dim_employee",
        "fact_production", "fact_sales", "fact_cost", "fact_inventory",
    ]
    return {f: pd.read_csv(os.path.join(RAW_DIR, f + ".csv")) for f in files}