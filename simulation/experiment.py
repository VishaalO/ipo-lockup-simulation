"""
experiment.py
Runs the full simulation experiment across 5 concentration scenarios.
Each scenario runs 200 iterations to produce stable statistics.

Scenarios (total insider ownership held constant at 30% across all):
  S1: 20 insiders, near-equal split.  Target HHI = 0.05
  S2: 10 insiders, near-equal split.  Target HHI = 0.10
  S3:  5 insiders, unequal split.     Target HHI = 0.25
  S4:  2 insiders, dominant/minor.    Target HHI = 0.52
  S5:  1 insider,  holds everything.  Target HHI = 1.00
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import pandas as pd
from model import IPOMarketModel

N_RUNS               = 200
TOTAL_SHARES         = 1_000_000
INSIDER_SHARE_FRAC   = 0.30
TOTAL_INSIDER_SHARES = int(TOTAL_SHARES * INSIDER_SHARE_FRAC)
N_RETAIL_TRADERS     = 150
IPO_PRICE            = 20.0
FUNDAMENTAL_VALUE    = 22.0

SCENARIOS = [
    {"label": "S1 — Very Low",  "n_insiders": 20, "target_hhi": 0.05, "color": "#1a7abf"},
    {"label": "S2 — Low",       "n_insiders": 10, "target_hhi": 0.10, "color": "#2ca05a"},
    {"label": "S3 — Medium",    "n_insiders":  5, "target_hhi": 0.25, "color": "#d4a017"},
    {"label": "S4 — High",      "n_insiders":  2, "target_hhi": 0.52, "color": "#d4611a"},
    {"label": "S5 — Very High", "n_insiders":  1, "target_hhi": 1.00, "color": "#b71c1c"},
]


def run_scenario(scenario: dict, n_runs: int, base_seed: int = 0) -> dict:
    sars        = []
    price_paths = []
    actual_hhis = []

    for i in range(n_runs):
        seed  = base_seed + i * 7
        model = IPOMarketModel(
            concentration_hhi    = scenario["target_hhi"],
            n_insiders           = scenario["n_insiders"],
            total_insider_shares = TOTAL_INSIDER_SHARES,
            n_retail_traders     = N_RETAIL_TRADERS,
            ipo_price            = IPO_PRICE,
            fundamental_value    = FUNDAMENTAL_VALUE,
            seed                 = seed,
        )
        model.run()
        sar = model.get_abnormal_return(window=5)
        if not np.isnan(sar):
            sars.append(sar)
        actual_hhis.append(model.simulated_hhi)
        price_paths.append(model.daily_prices[:])

    sars = np.array(sars)
    hhis = np.array(actual_hhis)
    min_len  = min(len(p) for p in price_paths)
    path_arr = np.array([p[:min_len] for p in price_paths])

    return {
        "label":      scenario["label"],
        "color":      scenario["color"],
        "target_hhi": scenario["target_hhi"],
        "actual_hhi": float(hhis.mean()),
        "n_insiders": scenario["n_insiders"],
        "n_valid":    len(sars),
        "sar_mean":   float(sars.mean()),
        "sar_median": float(np.median(sars)),
        "sar_std":    float(sars.std()),
        "sar_p5":     float(np.percentile(sars, 5)),
        "sar_p95":    float(np.percentile(sars, 95)),
        "sar_all":    sars.tolist(),
        "avg_path":   path_arr.mean(axis=0).tolist(),
        "std_path":   path_arr.std(axis=0).tolist(),
    }


def results_to_dataframe(results: list[dict]) -> pd.DataFrame:
    rows = []
    for r in results:
        rows.append({
            "Scenario":       r["label"],
            "N Insiders":     r["n_insiders"],
            "Target HHI":     r["target_hhi"],
            "Actual HHI":     round(r["actual_hhi"],  4),
            "SAR Mean (%)":   round(r["sar_mean"]   * 100, 3),
            "SAR Median (%)": round(r["sar_median"] * 100, 3),
            "SAR Std (%)":    round(r["sar_std"]    * 100, 3),
            "5th Pct (%)":    round(r["sar_p5"]     * 100, 3),
            "95th Pct (%)":   round(r["sar_p95"]    * 100, 3),
            "Valid Runs":     r["n_valid"],
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    import pickle

    print("\nIPO Lockup Simulation — Full Experiment")
    print("=" * 55)
    print(f"Scenarios:       {len(SCENARIOS)}")
    print(f"Iterations each: {N_RUNS}")
    print(f"Insider fraction: {INSIDER_SHARE_FRAC*100:.0f}%")
    print("=" * 55 + "\n")

    results = []
    for i, sc in enumerate(SCENARIOS):
        print(f"Running {sc['label']} (HHI={sc['target_hhi']:.2f}, "
              f"{sc['n_insiders']} insider(s))...", flush=True)
        r
