import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Demo-only synthetic training data. Replace with representative, verified company data.
_rng = np.random.default_rng(42)
_n = 600
_completion = _rng.uniform(10, 100, _n)
_days = _rng.integers(1, 180, _n)
_progress = _rng.uniform(0.1, 2.0, _n)
_cost = _rng.uniform(-5, 35, _n)

_project_x = np.column_stack([_completion, _days, _progress, _cost])
_project_y = ((_completion < 55) & (_days < 45) | (_progress < 0.45) | (_cost > 18)).astype(int)
_project_model = RandomForestClassifier(n_estimators=120, random_state=42)
_project_model.fit(_project_x, _project_y)

_revenue = _rng.uniform(50000, 500000, _n)
_expenses = _revenue * _rng.uniform(0.45, 1.15, _n)
_cash = _rng.uniform(10000, 300000, _n)
_debt = _rng.uniform(0, 400000, _n)
_finance_x = np.column_stack([_revenue, _expenses, _cash, _debt])
_finance_y = ((_expenses / _revenue > 0.9) | (_cash < _expenses * 0.18) | (_debt > _revenue * 0.65)).astype(int)
_finance_model = RandomForestClassifier(n_estimators=120, random_state=42)
_finance_model.fit(_finance_x, _finance_y)

def _level(p):
    if p >= 0.70:
        return "High"
    if p >= 0.40:
        return "Medium"
    return "Low"

def predict_project_risk(row):
    x = np.array([[
        float(row["completion_pct"]),
        float(row["days_remaining"]),
        float(row["weekly_progress"]),
        float(row["cost_variance_pct"])
    ]])
    p = float(_project_model.predict_proba(x)[0][1])
    actions = []
    if float(row["weekly_progress"]) < 0.5:
        actions.append("Review blockers and rebalance team workload.")
    if float(row["cost_variance_pct"]) > 15:
        actions.append("Review procurement and remaining project budget.")
    if float(row["days_remaining"]) < 30 and float(row["completion_pct"]) < 70:
        actions.append("Create a recovery schedule with weekly milestones.")
    if not actions:
        actions.append("Continue weekly monitoring and update project data.")
    return {"probability": p, "risk_level": _level(p), "recommendations": actions}

def predict_financial_risk(row):
    revenue = float(row["monthly_revenue"])
    expenses = float(row["monthly_expenses"])
    cash = float(row["cash_balance"])
    debt = float(row["debt"])
    x = np.array([[revenue, expenses, cash, debt]])
    p = float(_finance_model.predict_proba(x)[0][1])
    actions = []
    if revenue > 0 and expenses / revenue > 0.9:
        actions.append("Review major expense categories and identify savings.")
    if cash < expenses * 0.18:
        actions.append("Prepare a short-term cash-flow plan.")
    if revenue > 0 and debt / revenue > 0.65:
        actions.append("Review debt obligations and repayment schedule.")
    if not actions:
        actions.append("Maintain monthly financial monitoring.")
    return {"probability": p, "risk_level": _level(p), "recommendations": actions}
