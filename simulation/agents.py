"""
agents.py
Defines the three agent types in the IPO lockup simulation:
  1. InsiderAgent       - holds locked-up shares; decides to sell at/after expiration
  2. RetailTraderAgent  - models the general investing public
  3. MarketMakerAgent   - provides liquidity and sets price each step
"""

import numpy as np
from mesa import Agent


class InsiderAgent(Agent):
    def __init__(self, model, shares_held: int, sell_urgency: float):
        super().__init__(model)
        self.shares_held  = shares_held
        self.sell_urgency = sell_urgency
        self.has_sold     = False
        self.sold_day     = None
        mean_wait = max(1.0, 5.0 * (1.0 - sell_urgency))
        self.sell_day = int(np.random.exponential(mean_wait))

    def step(self):
        m = self.model
        if self.has_sold or m.current_day < m.LOCKUP_EXPIRATION:
            return
        days_since = m.current_day - m.LOCKUP_EXPIRATION
        if days_since >= self.sell_day:
            sell_frac = float(np.clip(np.random.beta(self.sell_urgency * 5 + 0.5, 2), 0.05, 1.0))
            shares_to_sell = max(1, int(self.shares_held * sell_frac))
            m.sell_orders.append({
                "shares": shares_to_sell,
                "agent_type": "insider",
                "urgency": self.sell_urgency,
            })
            self.has_sold = True
            self.sold_day = m.current_day


class RetailTraderAgent(Agent):
    def __init__(self, model, wealth, sentiment_bias, momentum_weight,
                 lockup_awareness, contrarian):
        super().__init__(model)
        self.wealth           = wealth
        self.sentiment_bias   = sentiment_bias
        self.momentum_weight  = momentum_weight
        self.lockup_awareness = lockup_awareness
        self.contrarian       = contrarian
        self.shares_owned     = 0

    def _momentum(self):
        p = self.model.price_history
        if len(p) < 3:
            return 0.0
        return float(np.clip((p[-1] - p[-3]) / (p[-3] + 1e-9) * 10, -1.0, 1.0))

    def _lockup_fear(self):
        days_to = self.model.LOCKUP_EXPIRATION - self.model.current_day
        hhi     = self.model.concentration_hhi
        if days_to > 10:
            base_fear = 0.0
        elif days_to >= 0:
            base_fear = (10 - days_to) / 10.0
        else:
            base_fear = max(0.0, 1.0 - abs(days_to) / 5.0)
        conc_amp = 1.0 + hhi * 2.5
        return base_fear * self.lockup_awareness * conc_amp

    def _herd(self):
        recent = self.model.recent_order_types[-20:]
        if len(recent) < 5:
            return 0.0
        return (recent.count("sell") / len(recent) - 0.5) * 0.6

    def step(self):
        m = self.model
        mom  = self._momentum()
        fear = self._lockup_fear()
        herd = self._herd()
        if self.contrarian > 0.5:
            mom  = -mom  * self.contrarian
            herd = -herd * self.contrarian
        desire = (self.momentum_weight * mom
                  + self.lockup_awareness * fear
                  + 0.15 * herd
                  - self.sentiment_bias * 0.3
                  + np.random.normal(0, 0.05))
        if abs(desire) < 0.12:
            return
        shares = max(1, int(self.wealth * np.random.uniform(0.01, 0.05)))
        if desire > 0:
            m.sell_orders.append({"shares": shares, "agent_type": "retail", "urgency": 0.5})
            m.recent_order_types.append("sell")
            self.shares_owned = max(0, self.shares_owned - shares)
        else:
            m.buy_orders.append({"shares": shares, "agent_type": "retail", "urgency": 0.5})
            m.recent_order_types.append("buy")
            self.shares_owned += shares


class MarketMakerAgent(Agent):
    def __init__(self, model, spread=0.00005, reversion_strength=0.02):
        super().__init__(model)
        self.spread             = spread
        self.reversion_strength = reversion_strength

    def step(self):
        m        = self.model
        buy_vol  = sum(o["shares"] for o in m.buy_orders)
        sell_vol = sum(o["shares"] for o in m.sell_orders)
        total    = max(1, buy_vol + sell_vol)
        net_imb  = sell_vol - buy_vol
        impact   = -self.spread * (net_imb / total) * 50
        revert   = self.reversion_strength * (
            m.fundamental_value - m.current_price) / m.fundamental_value
        insider_sells = sum(o["shares"] for o in m.sell_orders if o["agent_type"] == "insider")
        if insider_sells > 0:
            block_amp = 1.0 + (m.concentration_hhi ** 1.5) * 6.0
            impact += -self.spread * (insider_sells / total) * 50 * block_amp
        new_price = m.current_price * (1.0 + impact + revert)
        m.current_price = max(new_price, 0.01)
        m.price_history.append(m.current_price)
        if len(m.recent_order_types) > 200:
            m.recent_order_types = m.recent_order_types[-200:]
        m.buy_orders  = []
        m.sell_orders = []
