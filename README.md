# Insider Ownership Concentration and Post-Lockup Expiration Price Decay in IPO Markets
### An Agent-Based Simulation Study

**Author:** Vishaal O
**Status:** Under review — Journal of Emerging Investigators (JEI)
**Language:** Python 3.10+
**Method:** Agent-Based Simulation (Mesa 3.x)

---

## Overview

This repository contains the complete simulation code, results, and figures for the research paper:

> "Insider Ownership Concentration and Post-Lockup Expiration Price Decay in IPO Markets: An Agent-Based Simulation Approach"

### Research Question
Does higher insider ownership concentration — measured by the Herfindahl-Hirschman Index (HHI) — cause greater post-lockup expiration price decay in IPO markets, independent of total insider ownership levels?

### Key Finding
Yes. The simulation demonstrates a strong, statistically significant negative relationship between insider ownership concentration and post-lockup stock price performance (R2 = 0.9936, p = 0.0002). A company with all insider shares held by one person experiences a 44% larger price drop at lockup expiration than one where the same shares are spread across 20 insiders.

---

## Results at a Glance

| Scenario | Insiders | HHI | SAR Mean | SAR Std |
|----------|----------|-----|----------|---------|
| S1 Very Low | 20 | 0.050 | -2.097% | 0.099% |
| S2 Low | 10 | 0.100 | -2.094% | 0.152% |
| S3 Medium | 5 | 0.250 | -2.293% | 0.221% |
| S4 High | 2 | 0.517 | -2.601% | 0.351% |
| S5 Very High | 1 | 1.000 | -3.030% | 0.409% |

OLS Regression: SAR = -2.033% - 1.017% x HHI
R2 = 0.9936 | p = 0.0002 | S1 vs S5 t-test: t = 31.3, p = 0.000000

---

## How to Reproduce

Step 1 - Install dependencies

pip install -r requirements.txt

Step 2 - Run the full experiment (all 5 scenarios x 200 iterations)

cd simulation
python experiment.py

Step 3 - Generate all figures and statistical output

python analysis.py

---

## Key References

Field, L. C., and Hanka, G. (2001). The expiration of IPO share lockups. Journal of Finance, 56(2), 471-500.

Brav, A., and Gompers, P. A. (2003). The role of lockups in initial public offerings. Review of Financial Studies, 16(1), 1-29.

---

## License
MIT License - free to use and reproduce with attribution.
