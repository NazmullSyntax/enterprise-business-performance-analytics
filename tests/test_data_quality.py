import os
import pandas as pd

PROC = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


def test_no_negative_defects():
    df = pd.read_csv(os.path.join(PROC, "fact_production.csv"))
    assert (df.defect_units >= 0).all()


def test_no_duplicates():
    df = pd.read_csv(os.path.join(PROC, "fact_production.csv"))
    assert df.duplicated().sum() == 0


def test_no_null_downtime():
    df = pd.read_csv(os.path.join(PROC, "fact_production.csv"))
    assert df.downtime_minutes.notna().all()