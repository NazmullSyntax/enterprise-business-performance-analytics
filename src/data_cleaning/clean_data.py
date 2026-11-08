"""Clean raw synthetic data and write processed CSVs."""
import os
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
PROC_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")
os.makedirs(PROC_DIR, exist_ok=True)


def clean_production(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["factory_id"] = df["factory_id"].astype(str).str.upper()
    df = df[df["factory_id"].isin(["F01", "F02", "F03", "F04"])]
    df = df[df["machine_id"].str.match(r"^M\d{3}$") & (df["machine_id"] != "M999")]
    df["defect_units"] = df["defect_units"].clip(lower=0)
    df["downtime_minutes"] = df["downtime_minutes"].fillna(
        df["planned_minutes"] - df["run_minutes"])
    df = df.drop_duplicates()
    return df


def clean_sales(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df[df["units_sold"] > 0]
    df = df[df["revenue"] > 0]
    df = df.drop_duplicates()
    return df


def run():
    p = pd.read_csv(os.path.join(RAW_DIR, "fact_production.csv"))
    s = pd.read_csv(os.path.join(RAW_DIR, "fact_sales.csv"))
    clean_production(p).to_csv(os.path.join(PROC_DIR, "fact_production.csv"), index=False)
    clean_sales(s).to_csv(os.path.join(PROC_DIR, "fact_sales.csv"), index=False)
    print("Cleaned production and sales -> data/processed/")


if __name__ == "__main__":
    run()