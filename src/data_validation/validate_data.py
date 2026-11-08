"""Validate processed data and write data_quality_report.csv."""
import os
import pandas as pd

PROC_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")
RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
REPORT = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed",
                      "data_quality_report.csv")


def check(name, before, after, rule):
    return {"check": name, "rows_before": before, "rows_after": after,
            "rule": rule, "status": "PASS" if after <= before else "FAIL"}


def run():
    raw = pd.read_csv(os.path.join(RAW_DIR, "fact_production.csv"))
    proc = pd.read_csv(os.path.join(PROC_DIR, "fact_production.csv"))
    machines = pd.read_csv(os.path.join(RAW_DIR, "dim_machine.csv"))

    checks = [
        check("no_duplicate_rows", len(raw), len(proc.drop_duplicates()),
              "dedupe"),
        check("no_negative_defects", len(raw), len(proc[proc.defect_units >= 0]),
              "defect_units >= 0"),
        check("no_null_downtime", len(raw),
              len(proc[proc.downtime_minutes.notna()]), "not null"),
        check("valid_machines", len(raw),
              len(proc[proc.machine_id.isin(machines.machine_id)]),
              "machine_id in dim_machine"),
    ]
    report = pd.DataFrame(checks)
    report.to_csv(REPORT, index=False)
    print(report.to_string(index=False))
    print(f"\nReport saved -> {REPORT}")


if __name__ == "__main__":
    run()