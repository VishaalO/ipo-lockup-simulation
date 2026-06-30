"""
model.py
Core simulation engine. Runs a 230-day IPO market simulation.
Timeline:
  Days 0-39   : pre-IPO (no trading)
  Day 40      : IPO day (trading begins)
  Days 41-219 : lockup period (insiders cannot sell)
  Day 220     : lockup expiration (insiders free to sell)
  Days 221-229: post-expiration window
"""

import numpy as np
from mesa import Model
from agents import InsiderAgent, RetailTraderAgent, MarketMakerAgent


def _allocate_shares_by_hhi(n_insiders, total_shares, target_hhi, rng):
    if n_insiders == 1:
        return [total_shares]
    min_hhi = 1.0 / n_insiders
    if target_hhi <= min_hhi + 0.005:
        base   = total_shares // n_insiders
        extras = total_shares - base * n_insiders
        alloc  = [base + (1 if i < extras else 0) for i in range(n_insiders)]
        rng.shuffle(alloc)
        return alloc

    def sample_hhi(alpha):
        vals = [float(np.sum(rng.dirichlet([alpha]*n_insiders)**2)) for _ in range(200)]
        return float(np.mean(vals))

    lo, hi = 0.01, 20.0
    for _ in range(30):
        mid = (lo + hi) / 2
        if sample_hhi(mid) < target_hhi:
            hi = mid
        else:
            lo = mid
    fracs = rng.dirichlet([(lo+hi)/2] * n_insiders)
    raw   = (fracs * total_shares).astype(int)
    raw[0] += total_shares - int(raw.sum())
    return raw.tolist()


class IPOMarketModel(Model):

    IPO_DAY           = 40
    LOCKUP_EXPIRATION = 220
    TOTAL_DAYS        = 230

    def __init__(self, concentration_hhi=0.10, n_insiders=10,
                 total_insider_shares=300_000, n_retail_traders=150,
                 ipo_price=20.0, fundamental_value=22.0, seed=None):
        rng_arg = np.random.default_rng(seed)
        super().__init__(rng=rng_arg)

        self.concentration_hhi    = concentration_hhi
        self.total_insider_shares = total_insider_shares
        self.ipo_price            = ipo_price
        self.fundamental_value    = fundamental_value

        self.current_day   = 0
        self.current_price = ipo_price
        self.price_history = [ipo_price] * self.IPO_DAY

        self.buy_orders:         list = []
        self.sell_orders:        list = []
