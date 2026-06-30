"""
analysis.py
Statistical analysis and figure generation.
Loads simulation results and produces 5 publication-quality charts.
"""

import os
import sys
import pickle
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
CHARTS_DIR  = os.path.join(os.path.dirname(__file__), "..", "figures")
os.makedirs(CHARTS_DIR, exist_ok=True)

with open(os.path.join(RESULTS_DIR, "simulation_results.pkl"), "rb") as f:
    results = pickle.load(f)

plt.rcParams.update({
    "font.family":       "DejaVu Sans",
    "font.size":         11,
    "axes.titlesize":    13,
    "axes.titleweight":  "bold",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "figure.dpi":        150,
    "savefig.dpi":       180,
    "savefig.bbox":      "tight",
    "savefig.facecolor": "white",
})

COLORS = [r["color"] for r in results]
LABELS = [r["label"].split(" — ")[1] for r in results]
HHIS   = np.array([r["actual_hhi"] for r in results])
SARS   = np.array([r["sar_mean"]   for r in results]) * 100
STDS   = np.array([r["sar_std"]    for r in results]) * 100


# Figure 1 — SAR by Scenario
fig, ax = plt.subplots(figsize=(9, 5.5))
x    = np.arange(len(results))
bars = ax.bar(x, SARS, color=COLORS, width=0.55, zorder=3,
              edgecolor="white", linewidth=0.8)
n_runs = results[0]["n_valid"]
ci     = 1.96 * STDS / np.sqrt(n_runs)
ax.errorbar(x, SARS, yerr=ci, fmt="none", color="#333333",
            capsize=5, capthick=1.5, linewidth=1.5, zorder=4)
for bar, sar in zip(bars, SARS):
    ax.text(bar.get_x() + bar.get_width()/2, sar - 0.05,
            f"{sar:.2f}%", ha="center", va="top",
            fontsize=10, fontweight="bold", color="white")
ax.set_xticks(x)
ax.set_xticklabels(LABELS, fontsize=10)
ax.set_xlabel("Insider Ownership Concentration", labelpad=8)
ax.set_ylabel("Simulated Abnormal Return (%)", labelpad=8)
ax.set_title("Figure 1 — Post-Lockup Price Decay by Concentration Scenario\n"
             "(SAR over +/-2 day event window, 200 simulation runs per scenario)", pad=12)
ax.axhline(0, color="#999999", linewidth=0.8, linestyle="--")
ax.set_ylim(min(SARS) * 1.35, 0.3)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.1f}%"))
ax.grid(axis="y",
