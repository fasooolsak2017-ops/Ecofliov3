import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd

# ------------------------------
# Page config
# ------------------------------
st.set_page_config(
    page_title="EcoFolio – ESG Portfolio Optimiser",
    page_icon="🌿",
    layout="wide"
)

# ------------------------------
# Profile mappings
# ------------------------------
risk_profile_map = {
    "Cautious": 8,
    "Conservative": 5,
    "Balanced": 3,
    "Assertive": 1.5,
    "Aggressive": 0.75
}

esg_profile_map = {
    "Traditional Investor": 0.00,
    "ESG Aware Investor": 0.02,
    "Balanced Investor": 0.05,
    "Strong ESG Preference Investor": 0.10,
    "ESG-Focused Investor": 0.20
}

# ------------------------------
# Portfolio functions
# ------------------------------
def portfolio_ret(w1, r1, r2):
    return w1 * r1 + (1 - w1) * r2

def portfolio_sd(w1, sd1, sd2, rho):
    return np.sqrt(w1**2 * sd1**2 + (1-w1)**2 * sd2**2
                   + 2 * rho * w1 * (1-w1) * sd1 * sd2)

# =====================================================================
# GLOBAL STYLES
# =====================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Base ── */
html, body { font-family: 'Inter', sans-serif; }
#MainMenu, footer { visibility: hidden; }
.stApp { background: #f5f7f5; }

/* ── All main content text: dark, high-contrast ── */
.stApp { color: #1a202c; }
p, li, td, th, label, span, div { color: #1a202c; }
h1, h2, h3, h4 { color: #1b4332; font-weight: 700; }
[data-testid="stCaptionContainer"] p { color: #6b7280 !important; font-size: 13px !important; }
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] td,
[data-testid="stMarkdownContainer"] th { color: #1a202c !important; font-size: 15px; line-height: 1.75; }

/* ── Sidebar: dark green, light text ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1b4332 0%, #2d6a4f 100%) !important;
}
[data-testid="stSidebar"] p { color: #d8f3dc !important; }
[data-testid="stSidebar"] label { color: #b7e4c7 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #ffffff !important; }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: #95d5b2 !important; }
[data-testid="stSidebar"] hr { border-color: #40916c !important; }
[data-testid="stSidebar"] input { background: #ffffff !important; color: #1a202c !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #d8f3dc !important; font-size: 13px; }

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
    background: #ffffff;
    border-radius: 12px;
    padding: 4px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}
[data-testid="stTabs"] [role="tab"] {
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    color: #374151 !important;
    padding: 8px 18px !important;
    background: transparent !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: #2d6a4f !important;
    color: #ffffff !important;
    font-weight: 600 !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: #ffffff;
    border-radius: 12px;
    padding: 18px 22px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    border-top: 3px solid #2d6a4f;
}
[data-testid="stMetricLabel"] { font-size: 11px !important; color: #6b7280 !important; font-weight: 600 !important; text-transform: uppercase; letter-spacing: 0.07em; }
[data-testid="stMetricValue"] { font-size: 26px !important; font-weight: 700 !important; color: #1b4332 !important; }

/* ── Dataframes ── */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }

/* ── Expanders: outer container ── */
[data-testid="stExpander"] {
    border-radius: 12px !important;
    border: 1px solid #c6e6d0 !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06) !important;
    margin-bottom: 10px;
    overflow: hidden;
}
/* Body text */
[data-testid="stExpander"] [data-testid="stMarkdownContainer"] p,
[data-testid="stExpander"] [data-testid="stMarkdownContainer"] li,
[data-testid="stExpander"] [data-testid="stMarkdownContainer"] td,
[data-testid="stExpander"] [data-testid="stMarkdownContainer"] th { color: #1a202c !important; }

/* ── Alerts ── */
[data-testid="stAlert"] { border-radius: 10px !important; }

/* ── Input widgets in main area ── */
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea { color: #1a202c !important; }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# PAGE TITLE
# =====================================================================
st.markdown("""
<div style="
    background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 50%, #40916c 100%);
    border-radius: 16px;
    padding: 36px 40px;
    margin-bottom: 24px;
">
    <div style="font-size: 38px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;">
        🌿 EcoFolio
    </div>
    <div style="font-size: 16px; color: #b7e4c7; font-weight: 400; margin-top: 6px;">
        ESG Portfolio Optimiser &nbsp;&middot;&nbsp; Build sustainable, data-driven investment portfolios
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================================
# SIDEBAR – All inputs
# =====================================================================
st.sidebar.header("📊 Asset Inputs")

st.sidebar.subheader("Asset 1")
asset1_name = st.sidebar.text_input("Asset 1 Name", value="Tech ETF")
r_h   = st.sidebar.number_input(f"{asset1_name} Expected Return (%)", value=5.0, step=0.1) / 100
sd_h  = st.sidebar.number_input(f"{asset1_name} Standard Deviation (%)", value=9.0, min_value=0.01, step=0.1) / 100
esg_h = st.sidebar.number_input(f"{asset1_name} ESG Score (0–100)", value=60.0, min_value=0.0, max_value=100.0, step=1.0)

st.sidebar.subheader("Asset 2")
asset2_name = st.sidebar.text_input("Asset 2 Name", value="Green Bond")
r_f   = st.sidebar.number_input(f"{asset2_name} Expected Return (%)", value=12.0, step=0.1) / 100
sd_f  = st.sidebar.number_input(f"{asset2_name} Standard Deviation (%)", value=20.0, min_value=0.01, step=0.1) / 100
esg_f = st.sidebar.number_input(f"{asset2_name} ESG Score (0–100)", value=80.0, min_value=0.0, max_value=100.0, step=1.0)

st.sidebar.subheader("Market Parameters")
rho_hf = st.sidebar.slider("Correlation between assets", min_value=-1.0, max_value=1.0, value=-0.2, step=0.01)
r_free = st.sidebar.number_input("Risk-Free Rate (%)", value=2.0, min_value=0.0, max_value=30.0, step=0.1) / 100

# Warn if risk-free rate is unrealistically high
if r_free >= r_h or r_free >= r_f:
    st.sidebar.warning(
        f"⚠️ Risk-Free Rate ({r_free*100:.1f}%) is higher than one or both asset returns "
        f"({r_h*100:.1f}% / {r_f*100:.1f}%). Sharpe ratios will be negative and the "
        "tangency portfolio will be unreliable. Please enter a realistic risk-free rate."
    )

# ── ESG Minimum Constraint ──
st.sidebar.markdown("---")
st.sidebar.header("🛡️ ESG Minimum Constraint")
st.sidebar.caption("Exclude any portfolio whose weighted ESG score falls below this floor.")
esg_min_active = st.sidebar.toggle("Enable ESG Minimum", value=False)
if esg_min_active:
    esg_min_floor = st.sidebar.slider(
        "Minimum Portfolio ESG Score",
        min_value=0.0, max_value=100.0, value=50.0, step=0.5,
        help="Only portfolios with a weighted ESG score >= this value will be considered."
    )
    st.sidebar.caption(f"Active — portfolios with ESG score < **{esg_min_floor:.1f}** are excluded.")
else:
    esg_min_floor = 0.0

# ── ESG Questionnaire ──
st.sidebar.markdown("---")
st.sidebar.header("🌱 ESG Questionnaire")
st.sidebar.caption("Rate each statement from 1 (not important) to 10 (extremely important).")

env_score = st.sidebar.slider(
    "1. How important is environmental sustainability (e.g. carbon reduction, resource efficiency)?",
    min_value=1, max_value=10, value=5)
social_score = st.sidebar.slider(
    "2. How important are social factors (e.g. labour practices, diversity, community impact)?",
    min_value=1, max_value=10, value=5)
gov_score = st.sidebar.slider(
    "3. How important is strong corporate governance (e.g. transparency, ethical leadership)?",
    min_value=1, max_value=10, value=5)

total_esg_score = env_score + social_score + gov_score

if total_esg_score <= 8:
    esg_profile = "Traditional Investor"
    esg_description = (
        "ESG factors are not a primary consideration in your investment decisions. "
        "Your approach focuses mainly on financial performance."
    )
elif total_esg_score <= 14:
    esg_profile = "ESG Aware Investor"
    esg_description = (
        "ESG factors are considered in your investment decisions, particularly for "
        "identifying risks, but are not a central driver of your strategy."
    )
elif total_esg_score <= 20:
    esg_profile = "Balanced Investor"
    esg_description = (
        "ESG factors play a meaningful role alongside financial considerations. "
        "You aim to balance performance objectives with an interest in sustainability."
    )
elif total_esg_score <= 26:
    esg_profile = "Strong ESG Preference Investor"
    esg_description = (
        "ESG considerations are an important part of your investment decisions. "
        "You favour investments with stronger sustainability characteristics."
    )
else:
    esg_profile = "ESG-Focused Investor"
    esg_description = (
        "ESG outcomes are a central component of your investment approach. "
        "Your decisions place significant weight on environmental and social impact."
    )

lambda_esg = esg_profile_map[esg_profile]

# ── Risk Questionnaire ──
st.sidebar.markdown("---")
st.sidebar.header("⚖️ Risk Questionnaire")
st.sidebar.caption("1 = lean left, 10 = lean right.")

q1 = st.sidebar.slider(
    "1. If your investment fell 10%, would you sell (1) or buy more (10)?",
    min_value=1, max_value=10, value=5)
q2 = st.sidebar.slider(
    "2. Minimise risk (1) or maximise return with higher risk (10)?",
    min_value=1, max_value=10, value=5)
q3 = st.sidebar.slider(
    "3. How comfortable are you with large price fluctuations? (1=very uncomfortable, 10=very comfortable)",
    min_value=1, max_value=10, value=5)

total_risk_score = q1 + q2 + q3

if total_risk_score <= 8:
    risk_profile = "Cautious"
    risk_description = "You place strong importance on stability and are less comfortable with large losses."
elif total_risk_score <= 14:
    risk_profile = "Conservative"
    risk_description = "You are willing to take some risk, but protecting capital remains a higher priority."
elif total_risk_score <= 20:
    risk_profile = "Balanced"
    risk_description = "You seek a middle ground between stability and growth, accepting some volatility."
elif total_risk_score <= 26:
    risk_profile = "Assertive"
    risk_description = "You are comfortable taking on more risk in pursuit of stronger long-term growth."
else:
    risk_profile = "Aggressive"
    risk_description = "You are highly comfortable with market fluctuations and prioritise maximising returns."

gamma_risk = risk_profile_map[risk_profile]

# =====================================================================
# CALCULATIONS — Pedersen et al. (2021) direct optimisation
# Objective: max  x'μ − (γ/2) x'Σx + λ · s̄
# where s̄ = (x1·s1 + x2·s2) / (x1 + x2)  [portfolio-avg ESG, risky assets only]
# Constraints: x1 >= 0, x2 >= 0, x1 + x2 <= 1 (no leverage, no short-selling)
# Risk-free allocation = 1 − x1 − x2  (implicit)
# =====================================================================
from scipy.optimize import minimize as _minimize

# Build covariance matrix
_cov12  = rho_hf * sd_h * sd_f
_Sigma  = np.array([[sd_h**2, _cov12], [_cov12, sd_f**2]])
_mu     = np.array([r_h, r_f])
_esg_v  = np.array([esg_h, esg_f])

def _neg_obj(x):
    x1, x2 = x
    total = x1 + x2
    if total <= 1e-10:
        # all in risk-free
        return -(r_free)
    x_rf  = 1.0 - x1 - x2
    s_bar = (x1 * (_esg_v[0] / 100) + x2 * (_esg_v[1] / 100)) / total
    # full portfolio return including risk-free
    xT_mu    = x1 * _mu[0] + x2 * _mu[1] + x_rf * r_free
    xT_Sig_x = (x1**2 * _Sigma[0,0] + x2**2 * _Sigma[1,1]
                + 2 * x1 * x2 * _Sigma[0,1])
    return -(xT_mu - (gamma_risk / 2) * xT_Sig_x + lambda_esg * s_bar)

_bounds      = [(0.0, 1.0), (0.0, 1.0)]
_constraints = [{'type': 'ineq', 'fun': lambda x: 1.0 - x[0] - x[1]}]

# ESG minimum constraint: if active, add x1·s1 + x2·s2 >= floor · (x1+x2)
# i.e. (s1 - floor)·x1 + (s2 - floor)·x2 >= 0
if esg_min_active:
    # ESG floor constraint: weighted-avg ESG >= floor (on raw 0-100 scale, same as frontier)
    _constraints.append({
        'type': 'ineq',
        'fun': lambda x: ((esg_h - esg_min_floor) * x[0]
                         + (esg_f - esg_min_floor) * x[1])
    })

# Multi-start to avoid local optima
_starts = [(0.5,0.5),(0.3,0.3),(0.1,0.1),(0.4,0.4),(0.25,0.25),
           (0.2,0.6),(0.6,0.2),(0.1,0.8),(0.8,0.1),(0.0,0.5),(0.5,0.0)]
_best_val = -np.inf
_best_x   = np.array([0.0, 0.0])

for _x0 in _starts:
    _res = _minimize(_neg_obj, _x0, method='SLSQP',
                     bounds=_bounds, constraints=_constraints,
                     options={'ftol': 1e-14, 'maxiter': 10000})
    _val = -_res.fun
    if _val > _best_val:
        _best_val = _val
        _best_x   = _res.x

x1_optimal   = float(np.clip(_best_x[0], 0.0, 1.0))
x2_optimal   = float(np.clip(_best_x[1], 0.0, 1.0))
# Ensure sum constraint is exactly satisfied
if x1_optimal + x2_optimal > 1.0:
    _scale     = 1.0 / (x1_optimal + x2_optimal)
    x1_optimal *= _scale
    x2_optimal *= _scale
w_rf_optimal = 1.0 - x1_optimal - x2_optimal

# Rename to match rest of code
w1_optimal  = x1_optimal
w2_optimal  = x2_optimal

# Portfolio return and risk (risky portion + risk-free)
ret_optimal = w1_optimal * _mu[0] + w2_optimal * _mu[1] + w_rf_optimal * r_free
_x_vec      = np.array([w1_optimal, w2_optimal])
_var_opt    = float(_x_vec @ _Sigma @ _x_vec)
sd_optimal  = float(np.sqrt(_var_opt)) if _var_opt > 0 else 0.0

# Portfolio-average ESG (risky assets only)
_risky_total = w1_optimal + w2_optimal
esg_optimal  = ((w1_optimal * esg_h + w2_optimal * esg_f) / _risky_total
                if _risky_total > 1e-10 else 0.0)

# Objective value (Pedersen)
utility_optimal = _best_val  # objective value: x'μ - (γ/2)x'Σx + λ·s̄  (s̄ on [0,1])

# Tangency portfolio (for chart reference — unconstrained max-Sharpe blend)
_weights_t    = np.linspace(0, 1, 1000)
_sharpe_t     = []
for _w in _weights_t:
    _rt  = _w * r_h + (1 - _w) * r_f
    _sdt = np.sqrt(_w**2 * sd_h**2 + (1-_w)**2 * sd_f**2
                   + 2*_w*(1-_w)*rho_hf*sd_h*sd_f)
    _esg = _w * esg_h + (1 - _w) * esg_f
    if esg_min_active and _esg < esg_min_floor:
        _sharpe_t.append(-np.inf)
    else:
        _sharpe_t.append((_rt - r_free) / _sdt if _sdt > 0 else -np.inf)
_tang_idx    = int(np.argmax(_sharpe_t))
w1_tangency  = float(_weights_t[_tang_idx])
w2_tangency  = 1.0 - w1_tangency
ret_tangency = w1_tangency * r_h + w2_tangency * r_f
sd_tangency  = float(np.sqrt(w1_tangency**2 * sd_h**2 + w2_tangency**2 * sd_f**2
                              + 2*w1_tangency*w2_tangency*rho_hf*sd_h*sd_f))
esg_tangency = w1_tangency * esg_h + w2_tangency * esg_f
tang_ret_pct = ret_tangency * 100
tang_sd_pct  = sd_tangency * 100
tang_sr      = (ret_tangency - r_free) / sd_tangency if sd_tangency > 0 else 0

delta_ret = ret_tangency - ret_optimal
delta_esg = esg_optimal - esg_tangency

# Derived metrics
sharpe_optimal = (ret_optimal - r_free) / sd_optimal if sd_optimal > 0 else 0
sharpe_esg     = (ret_optimal + lambda_esg * (esg_optimal / 100) - r_free) / sd_optimal if sd_optimal > 0 else 0
pri_score      = esg_optimal

if esg_optimal >= 70:
    esg_level = "High ESG Impact"
elif esg_optimal >= 40:
    esg_level = "Medium ESG Impact"
else:
    esg_level = "Low ESG Impact"

# Corner solution flag
is_corner = (w1_optimal < 1e-4 or w2_optimal < 1e-4) and (w1_optimal + w2_optimal > 1e-4)

# Frontier data for charts
frontier_weights = np.linspace(0, 1, 1000)
frontier_returns, frontier_risks, frontier_esg, frontier_valid = [], [], [], []
for _w in frontier_weights:
    _ret = _w * r_h + (1 - _w) * r_f
    _sd  = np.sqrt(_w**2 * sd_h**2 + (1-_w)**2 * sd_f**2
                   + 2*_w*(1-_w)*rho_hf*sd_h*sd_f)
    _esg = _w * esg_h + (1 - _w) * esg_f
    frontier_returns.append(_ret * 100)
    frontier_risks.append(_sd * 100)
    frontier_esg.append(_esg)
    frontier_valid.append((not esg_min_active) or (_esg >= esg_min_floor))

frontier_returns = np.array(frontier_returns)
frontier_risks   = np.array(frontier_risks)
frontier_esg     = np.array(frontier_esg)
frontier_valid   = np.array(frontier_valid)
max_esg_idx      = int(np.argmax(frontier_esg))

# ESG-constrained frontier for comparison chart
esg_threshold = esg_min_floor if esg_min_active else (esg_h + esg_f) / 2
con_returns, con_risks = [], []
for _i, _w in enumerate(frontier_weights):
    if frontier_esg[_i] >= esg_threshold:
        con_returns.append(frontier_returns[_i])
        con_risks.append(frontier_risks[_i])
con_returns = np.array(con_returns)
con_risks   = np.array(con_risks)

if len(con_risks) > 0:
    _con_sr = [(con_returns[i]/100 - r_free) / (con_risks[i]/100)
               if con_risks[i] > 0 else -np.inf for i in range(len(con_risks))]
    _ct     = int(np.argmax(_con_sr))
    ct_ret, ct_sd, ct_sr = con_returns[_ct], con_risks[_ct], _con_sr[_ct]
else:
    ct_ret = ct_sd = ct_sr = 0.0

# Standalone outcomes
standalone_ret_1   = r_h
standalone_sd_1    = sd_h
standalone_esg_1   = esg_h
standalone_util_1  = standalone_ret_1 - 0.5 * gamma_risk * standalone_sd_1**2 + lambda_esg * (standalone_esg_1 / 100)
standalone_sharpe_1 = (standalone_ret_1 - r_free) / standalone_sd_1 if standalone_sd_1 > 0 else 0
standalone_esg_sharpe_1 = (standalone_ret_1 + lambda_esg*(standalone_esg_1/100) - r_free) / standalone_sd_1 if standalone_sd_1 > 0 else 0
standalone_ret_per_risk_1 = standalone_ret_1 / standalone_sd_1 if standalone_sd_1 > 0 else 0

standalone_ret_2   = r_f
standalone_sd_2    = sd_f
standalone_esg_2   = esg_f
standalone_util_2  = standalone_ret_2 - 0.5 * gamma_risk * standalone_sd_2**2 + lambda_esg * (standalone_esg_2 / 100)
standalone_sharpe_2 = (standalone_ret_2 - r_free) / standalone_sd_2 if standalone_sd_2 > 0 else 0
standalone_esg_sharpe_2 = (standalone_ret_2 + lambda_esg*(standalone_esg_2/100) - r_free) / standalone_sd_2 if standalone_sd_2 > 0 else 0
standalone_ret_per_risk_2 = standalone_ret_2 / standalone_sd_2 if standalone_sd_2 > 0 else 0

ret_per_risk_opt = ret_optimal / sd_optimal if sd_optimal > 0 else 0
sharpe_h = (r_h - r_free) / sd_h if sd_h > 0 else 0
sharpe_f = (r_f - r_free) / sd_f if sd_f > 0 else 0

# =====================================================================
# TABS
# =====================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📖 Guide",
    "👤 Investor Profile & Results",
    "📊 Portfolio Charts",
    "📋 Asset Comparison",
    "🔍 Portfolio Interpretation"
])

# ─────────────────────────────────────────────────────────────────────
# TAB 1 – User Guide
# ─────────────────────────────────────────────────────────────────────
with tab1:
    st.header("Welcome to EcoFolio 🌿")
    st.markdown(
        "EcoFolio is an **ESG-aware portfolio optimisation tool** that helps you build a "
        "two-asset investment portfolio that balances financial performance with your "
        "sustainability preferences."
    )

    st.info(
        "💡 **New here?** Complete the sidebar questionnaires, then use the tabs above "
        "to explore your personalised results.",
        icon="ℹ️"
    )

    st.markdown("---")

    # ── Step-by-step accordion ──────────────────────────────────────────
    st.subheader("📋 How it works – step by step")

    st.markdown("""
    <style>
    .eco-details {
        background: #ffffff;
        border: 1px solid #c6e6d0;
        border-radius: 12px;
        margin-bottom: 10px;
        overflow: hidden;
        font-family: 'Inter', sans-serif;
    }
    .eco-details summary {
        background: #e8f5e9;
        color: #1b4332;
        font-weight: 600;
        font-size: 15px;
        padding: 14px 20px;
        cursor: pointer;
        list-style: none;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .eco-details summary::-webkit-details-marker { display: none; }
    .eco-details summary::before {
        content: "▶";
        font-size: 11px;
        color: #2d6a4f;
        transition: transform 0.2s;
        display: inline-block;
    }
    .eco-details[open] summary::before { transform: rotate(90deg); }
    .eco-details summary:hover { background: #d1fae5; }
    .eco-details .eco-body {
        padding: 20px 24px;
        color: #1a202c;
        font-size: 15px;
        line-height: 1.75;
    }
    .eco-body p { color: #1a202c; margin-bottom: 10px; }
    .eco-body li { color: #1a202c; margin-bottom: 4px; }
    .eco-body table { width: 100%; border-collapse: collapse; margin: 12px 0; }
    .eco-body th { background: #e8f5e9; color: #1b4332; font-weight: 600; padding: 10px 14px; text-align: left; border: 1px solid #c6e6d0; }
    .eco-body td { color: #1a202c; padding: 9px 14px; border: 1px solid #e2e8f0; }
    .eco-body tr:nth-child(even) td { background: #f9fafb; }
    .eco-tip { color: #6b7280; font-size: 13px; margin-top: 12px; }
    </style>

    <details class="eco-details" open>
      <summary>Step 1 – Enter your asset details</summary>
      <div class="eco-body">
        <p>Open the <strong>sidebar</strong> (top section: <em>Asset Inputs</em>) and fill in:</p>
        <table>
          <tr><th>Field</th><th>What to enter</th></tr>
          <tr><td><strong>Asset Name</strong></td><td>A label, e.g. <em>Tech ETF</em> or <em>Green Bond</em></td></tr>
          <tr><td><strong>Expected Return (%)</strong></td><td>Annualised return you expect from the asset</td></tr>
          <tr><td><strong>Standard Deviation (%)</strong></td><td>Annualised volatility — higher = riskier</td></tr>
          <tr><td><strong>ESG Score (0–100)</strong></td><td>Sustainability rating for the asset</td></tr>
          <tr><td><strong>Correlation</strong></td><td>How the two assets move together (–1 to +1)</td></tr>
          <tr><td><strong>Risk-Free Rate (%)</strong></td><td>E.g. current T-bill / cash rate</td></tr>
        </table>
        <p class="eco-tip">💬 Tip: A negative correlation (e.g. –0.3) typically provides stronger diversification benefits.</p>
      </div>
    </details>

    <details class="eco-details">
      <summary>Step 2 – Complete the ESG Questionnaire</summary>
      <div class="eco-body">
        <p>Found in the sidebar under <strong>🌱 ESG Questionnaire</strong>.</p>
        <p>Rate <strong>three statements</strong> from 1 (not important) to 10 (extremely important) covering:</p>
        <ul>
          <li>🌍 Environmental sustainability</li>
          <li>🤝 Social factors</li>
          <li>🏛️ Corporate governance</li>
        </ul>
        <p>Your total score maps to one of five <strong>ESG Investor Profiles</strong>:</p>
        <table>
          <tr><th>Profile</th><th>Score Range</th><th>λ (ESG weight)</th></tr>
          <tr><td>Traditional Investor</td><td>3–8</td><td>0.00</td></tr>
          <tr><td>ESG Aware Investor</td><td>9–14</td><td>0.02</td></tr>
          <tr><td>Balanced Investor</td><td>15–20</td><td>0.05</td></tr>
          <tr><td>Strong ESG Preference</td><td>21–26</td><td>0.10</td></tr>
          <tr><td>ESG-Focused Investor</td><td>27–30</td><td>0.20</td></tr>
        </table>
      </div>
    </details>

    <details class="eco-details">
      <summary>Step 3 – Complete the Risk Questionnaire</summary>
      <div class="eco-body">
        <p>Found in the sidebar under <strong>⚖️ Risk Questionnaire</strong>.</p>
        <p>Answer <strong>three questions</strong> (1–10) about your attitude to losses and volatility. Your total score maps to a <strong>Risk Profile</strong>:</p>
        <table>
          <tr><th>Profile</th><th>Score Range</th><th>γ (risk aversion)</th></tr>
          <tr><td>Cautious</td><td>3–8</td><td>8</td></tr>
          <tr><td>Conservative</td><td>9–14</td><td>5</td></tr>
          <tr><td>Balanced</td><td>15–20</td><td>3</td></tr>
          <tr><td>Assertive</td><td>21–26</td><td>1.5</td></tr>
          <tr><td>Aggressive</td><td>27–30</td><td>0.75</td></tr>
        </table>
        <p class="eco-tip">Higher γ → model penalises risk more → portfolio shifts toward lower-volatility blends.</p>
      </div>
    </details>

    <details class="eco-details">
      <summary>Step 4 – View your results</summary>
      <div class="eco-body">
        <table>
          <tr><th>Tab</th><th>What you'll find</th></tr>
          <tr><td><strong>👤 Investor Profile & Results</strong></td><td>Your profile cards, optimal portfolio weights, and key metrics.</td></tr>
          <tr><td><strong>📊 Portfolio Charts</strong></td><td>Two ESG frontier charts with plain-English explanations.</td></tr>
          <tr><td><strong>📋 Asset Comparison</strong></td><td>Side-by-side tables for both assets and the optimal blend.</td></tr>
          <tr><td><strong>🔍 Portfolio Interpretation</strong></td><td>A plain-English summary of your personalised results.</td></tr>
        </table>
      </div>
    </details>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Key Concepts glossary ───────────────────────────────────────────
    st.subheader("📚 Key Concepts")
    st.caption("Click any term to expand its definition.")

    concepts = [
        ("📈 Efficient Frontier",
         "The set of portfolios that offer the <strong>highest expected return for a given level of risk</strong>. "
         "Any portfolio <em>not</em> on the frontier is suboptimal — you could get better return for the same risk, "
         "or the same return with less risk, by moving onto the frontier."),
        ("💎 Tangency Portfolio",
         "The portfolio on the frontier with the <strong>highest Sharpe Ratio</strong> — the best reward per unit "
         "of risk taken. It is the point where the Capital Market Line is tangent to the efficient frontier."),
        ("📐 Sharpe Ratio",
         "Defined as <strong>(Return − Risk-Free Rate) / Standard Deviation</strong>. It measures how much extra return "
         "you earn per unit of risk. Higher is better. A Sharpe of 1.0 means 1% excess return per 1% of volatility."),
        ("🌱 ESG Score (0–100)",
         "A composite measure of a fund's <strong>Environmental, Social, and Governance</strong> quality. "
         "Higher scores indicate stronger sustainability practices. EcoFolio uses a weighted average of your two assets' scores."),
        ("⭐ Optimal Portfolio",
         "The portfolio that <strong>maximises your personal utility function</strong>, combining expected return, "
         "risk aversion (γ), and ESG preference (λ). It is the blend recommended specifically for you."),
        ("📉 Capital Market Line (CML)",
         "The straight line from the <strong>risk-free rate</strong> through the <strong>Tangency Portfolio</strong>. "
         "Any point on this line is achievable by mixing the tangency portfolio with cash."),
        ("λ – ESG Preference Weight",
         "Controls how strongly the model rewards high ESG scores. λ = 0 means ESG has no influence; "
         "λ = 0.20 means sustainability is given significant weight alongside financial performance."),
        ("γ – Risk Aversion",
         "Controls how much the model penalises portfolio variance. "
         "High γ (e.g. 8 for <em>Cautious</em>) strongly discourages risky blends; "
         "low γ (e.g. 0.75 for <em>Aggressive</em>) allows more volatility in pursuit of return."),
    ]

    concept_html = ""
    for title, body in concepts:
        concept_html += f"""
        <details class="eco-details">
          <summary>{title}</summary>
          <div class="eco-body"><p>{body}</p></div>
        </details>"""
    st.markdown(concept_html, unsafe_allow_html=True)

    st.markdown("---")

    # ── ESG Minimum Constraint explainer ───────────────────────────────
    st.subheader("🛡️ ESG Minimum Constraint")

    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.markdown("""
        The **ESG Minimum Constraint** is an optional filter in the sidebar.
        When enabled, it **excludes any portfolio** whose weighted ESG score falls below the floor you set.

        **How to activate it:**
        1. Toggle **Enable ESG Minimum** to ON in the sidebar.
        2. Use the slider to set your minimum portfolio ESG score (0–100).
        3. All results update instantly.
        """)
    with col_right:
        st.markdown("**When to use it:**")
        st.success("✅ You have a firm sustainability policy — e.g. 'no portfolio below ESG 60'.")
        st.warning("📊 You want to quantify the return cost of enforcing a strict ESG floor.")
        st.info("🔀 You want to compare a constrained vs unconstrained strategy side by side.")

    st.markdown("""
    <details class="eco-details">
      <summary>What changes when the ESG Minimum is active?</summary>
      <div class="eco-body">
        <table>
          <tr><th>Element</th><th>Effect</th></tr>
          <tr><td><strong>Tangency Portfolio</strong></td><td>Shifts to the best risk-adjusted blend that still meets your ESG floor</td></tr>
          <tr><td><strong>Optimal Portfolio</strong></td><td>Chosen only from ESG-compliant blends</td></tr>
          <tr><td><strong>ESG Frontier Chart</strong></td><td>Excluded portfolios appear as grey dots</td></tr>
          <tr><td><strong>ESG vs MV Chart</strong></td><td>The green constrained curve uses your floor instead of the default midpoint</td></tr>
          <tr><td><strong>All result tabs</strong></td><td>A warning banner confirms the constraint is active</td></tr>
        </table>
      </div>
    </details>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Quick Tips ──────────────────────────────────────────────────────
    st.subheader("💡 Tips & Tricks")

    tip_col1, tip_col2, tip_col3 = st.columns(3)
    with tip_col1:
        st.info(
            "**Explore correlation effects**\n\n"
            "Try dragging the correlation slider toward –1. A strongly negative "
            "correlation shrinks portfolio risk dramatically — this is diversification at work."
        )
    with tip_col2:
        st.success(
            "**ESG score gap matters**\n\n"
            "If both assets have similar ESG scores, the ESG constraint will have "
            "little visible effect on the frontier comparison chart. A large gap makes "
            "the trade-off more visible."
        )
    with tip_col3:
        st.warning(
            "**Watch the risk-free rate**\n\n"
            "If the risk-free rate exceeds either asset's return, Sharpe ratios turn "
            "negative and the tangency portfolio becomes unreliable. Keep it realistic."
        )


# ─────────────────────────────────────────────────────────────────────
# TAB 2 – Investor Profile & Results
# ─────────────────────────────────────────────────────────────────────
with tab2:
    # ESG floor notice
    if esg_min_active:
        st.warning(f"🛡️ **ESG Minimum Constraint is active** — only portfolios with a weighted ESG score ≥ **{esg_min_floor:.1f}** are considered. Results below reflect this restriction.")

    if is_corner:
        low_asset  = asset1_name if w1_optimal < 1e-4 else asset2_name
        high_asset = asset2_name if w1_optimal < 1e-4 else asset1_name
        st.info(
            f"📐 **Corner Solution:** The optimiser has allocated 0% to **{low_asset}** and 100% of risky exposure to **{high_asset}**. "
            f"This is economically meaningful — at the current ESG preference (λ = {lambda_esg:.2f}), holding any of the lower-ESG asset is not optimal. "
            "The non-negativity constraint on that asset is binding. This is not a bug."
        )

    # Profile cards
    st.subheader("Your Investor Profile")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
            border-left: 5px solid #2e7d32;
            border-radius: 12px;
            padding: 24px 28px;
            height: 100%;
        ">
            <div style="font-size: 13px; font-weight: 600; color: #2e7d32; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px;">🌱 ESG Profile</div>
            <div style="font-size: 26px; font-weight: 700; color: #1b5e20; margin-bottom: 4px;">{esg_profile}</div>
            <div style="display: inline-block; background: #2e7d32; color: white; font-size: 13px; font-weight: 600; border-radius: 20px; padding: 3px 12px; margin-bottom: 14px;">Score: {total_esg_score} / 30</div>
            <div style="font-size: 14px; color: #33691e; line-height: 1.6;">{esg_description}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-left: 5px solid #1565c0;
            border-radius: 12px;
            padding: 24px 28px;
            height: 100%;
        ">
            <div style="font-size: 13px; font-weight: 600; color: #1565c0; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px;">⚖️ Risk Profile</div>
            <div style="font-size: 26px; font-weight: 700; color: #0d47a1; margin-bottom: 4px;">{risk_profile}</div>
            <div style="display: inline-block; background: #1565c0; color: white; font-size: 13px; font-weight: 600; border-radius: 20px; padding: 3px 12px; margin-bottom: 14px;">Score: {total_risk_score} / 30</div>
            <div style="font-size: 14px; color: #1a237e; line-height: 1.6;">{risk_description}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 16px'></div>", unsafe_allow_html=True)
    st.markdown("---")

    # Optimal portfolio metrics
    st.markdown("""
    <div style="font-size:20px; font-weight:700; color:#1b4332; margin-bottom:12px;">
        📈 Optimal Portfolio Results
    </div>
    """, unsafe_allow_html=True)
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Expected Return",  f"{ret_optimal*100:.2f}%")
    m2.metric("Portfolio Risk",   f"{sd_optimal*100:.2f}%")
    m3.metric("Sharpe Ratio",     f"{sharpe_optimal:.3f}")
    m4.metric("ESG Score",        f"{esg_optimal:.1f}")
    m5.metric("Investor Utility", f"{utility_optimal:.4f}")

    st.markdown("---")

    # Portfolio weights
    st.markdown("""
    <div style="font-size:20px; font-weight:700; color:#1b4332; margin-bottom:12px;">
        ⚖️ Portfolio Weights
    </div>
    """, unsafe_allow_html=True)
    wc1, wc2, wc3 = st.columns(3)
    wc1.metric("Risk-Free Asset", f"{w_rf_optimal*100:.2f}%")
    wc2.metric(asset1_name,       f"{w1_optimal*100:.2f}%")
    wc3.metric(asset2_name,       f"{w2_optimal*100:.2f}%")

# ─────────────────────────────────────────────────────────────────────
# TAB 3 – Portfolio Charts
# ─────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("📊 Portfolio Charts")
    if esg_min_active:
        st.warning(f"🛡️ **ESG Minimum active ({esg_min_floor:.1f})** — greyed-out dots on the left chart are excluded portfolios. The green curve on the right reflects your ESG floor.")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6.5))

    # LEFT PANEL: ESG-Efficient Frontier
    # Split frontier into valid (passes floor) and excluded dots
    if esg_min_active:
        # Excluded (greyed out)
        ax1.scatter(frontier_risks[~frontier_valid], frontier_returns[~frontier_valid],
                    color="lightgrey", s=6, zorder=1, alpha=0.35, label="Excluded (ESG < floor)")
        # Valid (colour-coded)
        sc_valid = ax1.scatter(frontier_risks[frontier_valid], frontier_returns[frontier_valid],
                               c=frontier_esg[frontier_valid], cmap="RdYlGn", s=8, zorder=2,
                               alpha=0.85, label="Frontier portfolios (ESG ≥ floor)",
                               vmin=frontier_esg.min(), vmax=frontier_esg.max())
        cbar = fig.colorbar(sc_valid, ax=ax1, pad=0.02)
    else:
        scatter = ax1.scatter(frontier_risks, frontier_returns, c=frontier_esg,
                              cmap="RdYlGn", s=8, zorder=2, label="Frontier portfolios")
        cbar = fig.colorbar(scatter, ax=ax1, pad=0.02)
    cbar.set_label("ESG Score", fontsize=10)

    max_sharpe_ratio = (ret_tangency - r_free) / sd_tangency if sd_tangency > 0 else 0
    cml_x_max = max(frontier_risks) * 1.2
    ax1.plot([0, cml_x_max],
             [r_free * 100, r_free * 100 + max_sharpe_ratio * cml_x_max],
             "--", color="grey", linewidth=1, alpha=0.7, label="CML", zorder=1)

    ax1.scatter([0], [r_free * 100], color="blue", s=100, marker="o",
                edgecolors="black", zorder=5, label=f"Risk-Free ({r_free*100:.1f}%)")
    ax1.scatter([sd_tangency * 100], [ret_tangency * 100], color="gold", s=180,
                marker="D", edgecolors="black", linewidths=0.8, zorder=5,
                label="Tangency / Max Sharpe")
    ax1.scatter([frontier_risks[max_esg_idx]], [frontier_returns[max_esg_idx]],
                color="green", s=180, marker="^", edgecolors="black",
                linewidths=0.8, zorder=5, label="Max ESG")
    ax1.scatter([sd_optimal * 100], [ret_optimal * 100], color="red", s=280,
                marker="*", edgecolors="black", linewidths=0.8, zorder=6,
                label=f"Optimal (w\u2081={w1_optimal*100:.1f}%)")

    ax1.set_xlabel("Portfolio Std Dev (%)", fontsize=11)
    ax1.set_ylabel("Expected Return (%)", fontsize=11)
    ax1.set_title("ESG-Efficient Frontier: Risk vs Return", fontsize=13, fontweight="bold")
    ax1.legend(loc="upper left", fontsize=7.5, framealpha=0.9)
    ax1.grid(True, alpha=0.3)

    # RIGHT PANEL: ESG vs Mean-Variance Frontier
    x_max = max(frontier_risks) * 1.25

    ax2.plot(frontier_risks, frontier_returns,
             color="steelblue", linewidth=2.5,
             label="Mean-Variance Frontier (all assets)")
    cml_u_y = [r_free * 100 + tang_sr * x for x in [0, x_max]]
    ax2.plot([0, x_max], cml_u_y,
             "--", color="steelblue", linewidth=1.3, alpha=0.75,
             label="Cap. Market Line (all assets)")
    ax2.scatter([tang_sd_pct], [tang_ret_pct],
                color="steelblue", s=160, marker="D",
                edgecolors="black", linewidths=0.8, zorder=5,
                label="Tangency portfolio (all assets)")

    if len(con_risks) > 0:
        frontier_label = f"MV Frontier (ESG \u2265 {esg_threshold:.0f}{' — your floor' if esg_min_active else ' — default midpoint'})"
        ax2.plot(con_risks, con_returns,
                 color="seagreen", linewidth=2.5,
                 label=frontier_label)
        cml_c_y = [r_free * 100 + ct_sr * x for x in [0, x_max]]
        ax2.plot([0, x_max], cml_c_y,
                 "--", color="seagreen", linewidth=1.3, alpha=0.75,
                 label="Cap. Market Line (ESG constrained)")
        ax2.scatter([ct_sd], [ct_ret],
                    color="seagreen", s=160, marker="D",
                    edgecolors="black", linewidths=0.8, zorder=5,
                    label="Tangency portfolio (ESG constrained)")

    ax2.scatter([0], [r_free * 100],
                color="black", s=80, zorder=6,
                label=f"Risk-Free ({r_free*100:.1f}%)")
    ax2.annotate("Tangency\n(all assets)",
                 xy=(tang_sd_pct, tang_ret_pct),
                 xytext=(tang_sd_pct + 1, tang_ret_pct - 0.5),
                 fontsize=8, color="steelblue",
                 arrowprops=dict(arrowstyle="->", color="steelblue", lw=0.8))
    if len(con_risks) > 0:
        ax2.annotate("Tangency\n(ESG constrained)",
                     xy=(ct_sd, ct_ret),
                     xytext=(ct_sd + 1, ct_ret + 0.4),
                     fontsize=8, color="seagreen",
                     arrowprops=dict(arrowstyle="->", color="seagreen", lw=0.8))

    ax2.set_xlabel("Portfolio Std Dev (%)", fontsize=11)
    ax2.set_ylabel("Expected Return (%)", fontsize=11)
    ax2.set_title("ESG-Efficient Frontier vs Mean-Variance Frontier",
                  fontsize=13, fontweight="bold")
    ax2.legend(loc="upper left", fontsize=8.5, framealpha=0.9)
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    # Chart explanations
    st.markdown("---")
    exp_col1, exp_col2 = st.columns(2)

    with exp_col1:
        st.markdown("""
        <details class="eco-details">
          <summary>📌 About this chart – ESG-Efficient Frontier: Risk vs Return</summary>
          <div class="eco-body">
            <p>This chart maps every possible blend of your two assets onto a risk/return plane.
            Each dot represents a different portfolio, colour-coded from <strong>red (low ESG)</strong> to
            <strong>green (high ESG)</strong> based on its weighted ESG score.</p>
            <ul>
              <li>The <strong>grey dashed line (CML)</strong> is the Capital Market Line — it passes through the risk-free rate and the tangency portfolio, showing the best risk/return trade-off available by combining the risky portfolio with cash.</li>
              <li>The <strong>gold diamond</strong> marks the <strong>Tangency Portfolio</strong> — the risky-asset blend with the highest Sharpe Ratio, ignoring ESG preferences.</li>
              <li>The <strong>green triangle</strong> marks the <strong>Max ESG Portfolio</strong> — the blend with the highest combined ESG score, regardless of financial performance.</li>
              <li>The <strong>red star</strong> is <strong>your Optimal Portfolio</strong> — the point that maximises your personal utility function, weighing return, risk tolerance, and ESG preference.</li>
            </ul>
            <p><strong>Why it matters:</strong> It shows where your personalised recommendation sits on the frontier and whether you are trading financial return for sustainability — or whether the two align.</p>
          </div>
        </details>
        """, unsafe_allow_html=True)

    with exp_col2:
        floor_note = f"Your <strong>ESG Minimum of {esg_min_floor:.1f}</strong> is active, so the green curve shows only portfolios meeting your floor." if esg_min_active else f"The midpoint threshold of <strong>{esg_threshold:.0f}</strong> (average of your two asset ESG scores) is used as the default floor."
        st.markdown(f"""
        <details class="eco-details">
          <summary>📌 About this chart – ESG-Efficient Frontier vs Mean-Variance Frontier</summary>
          <div class="eco-body">
            <p>This chart overlays two separate efficient frontiers so you can see the impact of applying an ESG constraint to your portfolio.</p>
            <ul>
              <li>The <strong>blue curve</strong> is the <strong>unconstrained Mean-Variance Frontier</strong> — the full range of risk/return trade-offs using any blend of the two assets.</li>
              <li>The <strong>green curve</strong> is the <strong>ESG-Constrained Frontier</strong> — {floor_note}</li>
              <li>Each frontier has its own <strong>tangency portfolio (diamond)</strong> and <strong>Capital Market Line (dashed)</strong>, representing the best risk-adjusted return available under each set of constraints.</li>
            </ul>
            <p><strong>Why it matters:</strong> If the green (ESG) frontier sits noticeably <em>below</em> the blue (unconstrained) frontier, imposing an ESG floor comes at a financial cost. If the two curves largely overlap, sustainable investing does <strong>not</strong> meaningfully reduce your risk-adjusted returns. The gap between the two tangency points quantifies the price of sustainability.</p>
          </div>
        </details>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────
# TAB 4 – Asset Comparison
# ─────────────────────────────────────────────────────────────────────
with tab4:
    if esg_min_active:
        st.warning(f"🛡️ **ESG Minimum active ({esg_min_floor:.1f})** — optimal weights and metrics reflect the ESG floor constraint.")
    st.markdown('<div style="font-size:20px; font-weight:700; color:#1b4332; margin-bottom:12px;">📋 Asset Comparison</div>', unsafe_allow_html=True)

    comparison_df = pd.DataFrame({
        "Metric": ["Expected Return (%)", "Standard Deviation (%)", "ESG Score",
                   "Sharpe Ratio", "Tangency Weight (%)", "Optimal Portfolio Weight (%)"],
        asset1_name: [f"{r_h*100:.2f}", f"{sd_h*100:.2f}", f"{esg_h:.2f}",
                      f"{sharpe_h:.3f}", f"{w1_tangency*100:.2f}", f"{w1_optimal*100:.2f}"],
        asset2_name: [f"{r_f*100:.2f}", f"{sd_f*100:.2f}", f"{esg_f:.2f}",
                      f"{sharpe_f:.3f}", f"{w2_tangency*100:.2f}", f"{w2_optimal*100:.2f}"],
    })
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown('<div style="font-size:20px; font-weight:700; color:#1b4332; margin-bottom:4px;">📋 Asset Outcomes Comparison</div>', unsafe_allow_html=True)
    st.caption("Hypothetical 100% allocation to each asset vs the Optimal Portfolio blend.")

    outcomes_df = pd.DataFrame({
        "Metric": ["Expected Return (%)", "Portfolio Risk / Std Dev (%)", "Sharpe Ratio",
                   "ESG Score", "ESG-Adjusted Sharpe Ratio", "Return per Unit of Risk",
                   "Investor Utility Score"],
        asset1_name: [f"{standalone_ret_1*100:.2f}", f"{standalone_sd_1*100:.2f}",
                      f"{standalone_sharpe_1:.3f}", f"{standalone_esg_1:.2f}",
                      f"{standalone_esg_sharpe_1:.3f}", f"{standalone_ret_per_risk_1:.3f}",
                      f"{standalone_util_1:.4f}"],
        asset2_name: [f"{standalone_ret_2*100:.2f}", f"{standalone_sd_2*100:.2f}",
                      f"{standalone_sharpe_2:.3f}", f"{standalone_esg_2:.2f}",
                      f"{standalone_esg_sharpe_2:.3f}", f"{standalone_ret_per_risk_2:.3f}",
                      f"{standalone_util_2:.4f}"],
        "Optimal Blend": [f"{ret_optimal*100:.2f}", f"{sd_optimal*100:.2f}",
                          f"{sharpe_optimal:.3f}", f"{esg_optimal:.2f}",
                          f"{sharpe_esg:.3f}", f"{ret_per_risk_opt:.3f}",
                          f"{utility_optimal:.4f}"],
    })
    st.dataframe(outcomes_df, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────
# TAB 5 – Portfolio Interpretation
# ─────────────────────────────────────────────────────────────────────
with tab5:
    st.markdown("""
    <div style="font-size:22px; font-weight:700; color:#1b4332; margin-bottom:4px;">
        🔍 Portfolio Interpretation
    </div>
    """, unsafe_allow_html=True)
    if esg_min_active:
        st.warning(f"🛡️ **ESG Minimum active ({esg_min_floor:.1f})** — the interpretation below accounts for the ESG floor constraint.")

    st.markdown(f"""
    <div style="background:#ffffff; border-radius:14px; padding:28px 32px; box-shadow:0 2px 8px rgba(0,0,0,0.06); margin-bottom:20px; line-height:1.8; color:#2d3748; font-size:15px;">
        The recommended portfolio reflects your selected risk tolerance and sustainability preferences.
        Based on your questionnaire responses (<strong>{risk_profile} risk profile</strong>, <strong>{esg_profile}</strong>),
        the model maximises a utility function that balances expected return, portfolio risk, and ESG impact.
        <br><br>
        <ul style="margin:0; padding-left:20px;">
            <li>The portfolio delivers an <strong>expected return of {ret_optimal*100:.2f}%</strong> with a <strong>volatility of {sd_optimal*100:.2f}%</strong>.</li>
            <li>The <strong>Sharpe Ratio of {sharpe_optimal:.3f}</strong> reflects the risk-adjusted financial performance.</li>
            <li>The <strong>ESG-adjusted Sharpe Ratio is {sharpe_esg:.3f}</strong>, incorporating sustainability-adjusted performance.</li>
            <li>The <strong>portfolio ESG score is {esg_optimal:.2f}</strong>, corresponding to a <strong>{esg_level.lower()}</strong>.</li>
            <li>Relative to the maximum Sharpe portfolio, you sacrifice <strong>{-delta_ret*100:.2f}% of expected return</strong>
            in exchange for an <strong>ESG improvement of {delta_esg:.2f} points</strong>.</li>
        </ul>
        <br>
        Overall, the allocation balances financial performance with sustainability preferences in line with your questionnaire responses.
    </div>
    """, unsafe_allow_html=True)

    if utility_optimal >= standalone_util_1 and utility_optimal >= standalone_util_2:
        st.success("✅ The Optimal Blend outperforms **both** standalone assets on utility.")
    elif utility_optimal >= standalone_util_1:
        st.warning(f"✅ The Optimal Blend outperforms **{asset1_name}** on utility.  \n"
                   f"⚠️ {asset2_name} standalone has higher utility — consider ESG / risk trade-offs.")
    elif utility_optimal >= standalone_util_2:
        st.warning(f"✅ The Optimal Blend outperforms **{asset2_name}** on utility.  \n"
                   f"⚠️ {asset1_name} standalone has higher utility — consider ESG / risk trade-offs.")
    else:
        st.warning("⚠️ Both standalone assets show higher raw utility — the blend adds diversification value.")

st.markdown("""
<div style="
    background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%);
    border-radius: 12px;
    padding: 18px 28px;
    margin-top: 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
">
    <span style="color:#b7e4c7; font-size:14px;">🌿 <strong style="color:white;">EcoFolio</strong> — ESG Portfolio Optimiser</span>
    <span style="color:#74c69d; font-size:13px;">Built with Streamlit &amp; NumPy</span>
</div>
""", unsafe_allow_html=True)
