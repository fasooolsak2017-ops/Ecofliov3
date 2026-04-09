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
    "Traditional Investor": 0.1,
    "ESG Aware Investor": 0.3,
    "Balanced Investor": 0.5,
    "Strong ESG Preference Investor": 0.7,
    "ESG-Focused Investor": 0.9
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
# PAGE TITLE
# =====================================================================
st.title("🌿 EcoFolio – ESG Portfolio Optimiser")
st.markdown("---")

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
r_free = st.sidebar.number_input("Risk-Free Rate (%)", value=2.0, step=0.1) / 100

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
# CALCULATIONS (run once, before tabs)
# =====================================================================

# Tangency Portfolio — respects ESG minimum if active
weights_t = np.linspace(0, 1, 1000)
sharpe_ratios = []
for w in weights_t:
    ret = portfolio_ret(w, r_h, r_f)
    sd  = portfolio_sd(w, sd_h, sd_f, rho_hf)
    esg = w * esg_h + (1 - w) * esg_f
    # If ESG floor is active and this blend fails it, exclude from tangency search
    if esg_min_active and esg < esg_min_floor:
        sharpe_ratios.append(-np.inf)
    else:
        sharpe_ratios.append((ret - r_free) / sd if sd > 0 else -np.inf)

max_idx      = np.argmax(sharpe_ratios)
w1_tangency  = weights_t[max_idx]
w2_tangency  = 1 - w1_tangency
ret_tangency = portfolio_ret(w1_tangency, r_h, r_f)
sd_tangency  = portfolio_sd(w1_tangency, sd_h, sd_f, rho_hf)

# Optimal Portfolio (Utility Maximisation with ESG) — respects ESG minimum if active
weights_u    = np.linspace(0, 1, 1000)  # no leverage: total allocation <= 100%
utilities    = []
returns_u    = []
risks_u      = []
esg_scores_u = []

for w in weights_u:
    w1  = w * w1_tangency
    w2  = w * w2_tangency
    ret = r_free + w * (ret_tangency - r_free)
    sd  = abs(w) * sd_tangency
    esg = w1 * esg_h + w2 * esg_f
    # If ESG floor is active and this blend fails it, exclude from utility search
    if esg_min_active and esg < esg_min_floor:
        utilities.append(-np.inf)
    else:
        utilities.append(ret - 0.5 * gamma_risk * sd**2 + lambda_esg * (esg / 100))
    returns_u.append(ret)
    risks_u.append(sd)
    esg_scores_u.append(esg)

optimal_idx     = np.argmax(utilities)
w_optimal       = weights_u[optimal_idx]
w1_optimal      = w_optimal * w1_tangency
w2_optimal      = w_optimal * w2_tangency
w_rf_optimal    = 1 - w_optimal
ret_optimal     = returns_u[optimal_idx]
sd_optimal      = risks_u[optimal_idx]
esg_optimal     = esg_scores_u[optimal_idx]
utility_optimal = utilities[optimal_idx]

# Normalise weights so they always sum to exactly 100%
_total       = w1_optimal + w2_optimal + w_rf_optimal
w1_optimal   /= _total
w2_optimal   /= _total
w_rf_optimal /= _total

# Derived metrics
sharpe_optimal = (ret_optimal - r_free) / sd_optimal if sd_optimal > 0 else 0
sharpe_esg     = (ret_optimal + lambda_esg * (esg_optimal / 100) - r_free) / sd_optimal if sd_optimal > 0 else 0
pri_score      = (esg_optimal / 100) * 100

if esg_optimal >= 70:
    esg_level = "High ESG Impact"
elif esg_optimal >= 40:
    esg_level = "Medium ESG Impact"
else:
    esg_level = "Low ESG Impact"

esg_tangency = w1_tangency * esg_h + w2_tangency * esg_f
delta_ret    = ret_tangency - ret_optimal
delta_esg    = esg_optimal - esg_tangency

# Frontier data — all blends (for plotting); mark excluded ones
frontier_weights = np.linspace(0, 1, 1000)
frontier_returns = []
frontier_risks   = []
frontier_esg     = []
frontier_valid   = []  # True if blend passes the ESG floor (or floor is off)

for w in frontier_weights:
    ret = portfolio_ret(w, r_h, r_f)
    sd  = portfolio_sd(w, sd_h, sd_f, rho_hf)
    esg = w * esg_h + (1 - w) * esg_f
    frontier_returns.append(ret * 100)
    frontier_risks.append(sd * 100)
    frontier_esg.append(esg)
    frontier_valid.append((not esg_min_active) or (esg >= esg_min_floor))

frontier_returns = np.array(frontier_returns)
frontier_risks   = np.array(frontier_risks)
frontier_esg     = np.array(frontier_esg)
frontier_valid   = np.array(frontier_valid)
max_esg_idx      = np.argmax(frontier_esg)

# ESG-constrained frontier for the comparison chart:
# use the user-set floor if active, otherwise use the midpoint default
esg_threshold = esg_min_floor if esg_min_active else (esg_h + esg_f) / 2
con_returns, con_risks = [], []
for i, w in enumerate(frontier_weights):
    esg = w * esg_h + (1 - w) * esg_f
    if esg >= esg_threshold:
        con_returns.append(frontier_returns[i])
        con_risks.append(frontier_risks[i])

con_returns = np.array(con_returns)
con_risks   = np.array(con_risks)

tang_ret_pct = ret_tangency * 100
tang_sd_pct  = sd_tangency * 100
tang_sr      = (ret_tangency - r_free) / sd_tangency if sd_tangency > 0 else 0

if len(con_risks) > 0:
    con_sharpes = [
        (con_returns[i] / 100 - r_free) / (con_risks[i] / 100)
        if con_risks[i] > 0 else -np.inf
        for i in range(len(con_risks))
    ]
    ct_idx = np.argmax(con_sharpes)
    ct_ret = con_returns[ct_idx]
    ct_sd  = con_risks[ct_idx]
    ct_sr  = con_sharpes[ct_idx]
else:
    ct_ret = ct_sd = ct_sr = 0

# Standalone outcomes (used in tabs 4 & 5)
standalone_ret_1  = r_free + 1.0 * (r_h - r_free)
standalone_sd_1   = sd_h
standalone_esg_1  = esg_h
standalone_util_1 = standalone_ret_1 - 0.5 * gamma_risk * standalone_sd_1**2 + lambda_esg * (standalone_esg_1 / 100)
standalone_sharpe_1 = (standalone_ret_1 - r_free) / standalone_sd_1 if standalone_sd_1 > 0 else 0
standalone_esg_sharpe_1 = (standalone_ret_1 + lambda_esg * (standalone_esg_1 / 100) - r_free) / standalone_sd_1 if standalone_sd_1 > 0 else 0
standalone_ret_per_risk_1 = standalone_ret_1 / standalone_sd_1 if standalone_sd_1 > 0 else 0

standalone_ret_2  = r_free + 1.0 * (r_f - r_free)
standalone_sd_2   = sd_f
standalone_esg_2  = esg_f
standalone_util_2 = standalone_ret_2 - 0.5 * gamma_risk * standalone_sd_2**2 + lambda_esg * (standalone_esg_2 / 100)
standalone_sharpe_2 = (standalone_ret_2 - r_free) / standalone_sd_2 if standalone_sd_2 > 0 else 0
standalone_esg_sharpe_2 = (standalone_ret_2 + lambda_esg * (standalone_esg_2 / 100) - r_free) / standalone_sd_2 if standalone_sd_2 > 0 else 0
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
    st.header("Welcome to EcoFolio")
    st.markdown("""
    EcoFolio is an **ESG-aware portfolio optimisation tool** that helps you build a two-asset
    investment portfolio that balances financial performance with your sustainability preferences.

    ---

    ### How it works – step by step

    **Step 1 – Enter your asset details** (sidebar, top section)
    - Give each asset a name (e.g. *Tech ETF*, *Green Bond*).
    - Enter the **expected annual return (%)**, **standard deviation / volatility (%)**, and
      **ESG score (0–100)** for each asset.
    - Enter the **correlation** between the two assets (–1 to +1) and the **risk-free rate (%)**.

    **Step 2 – Complete the ESG Questionnaire** (sidebar, middle section)
    - Rate three statements (1–10) about how important Environmental, Social, and Governance
      factors are to you when investing.
    - Your total score determines your **ESG Investor Profile**, which influences how much the
      model rewards sustainability in the portfolio.

    **Step 3 – Complete the Risk Questionnaire** (sidebar, bottom section)
    - Answer three questions (1–10) about your attitude to investment losses and volatility.
    - Your total score determines your **Risk Profile**, which controls how much the model
      penalises portfolio risk.

    **Step 4 – View the results**
    - Use the tabs above to navigate between your results:
        - **Investor Profile & Results** — your profile cards, optimal portfolio metrics, and weights.
        - **Portfolio Charts** — two ESG frontier charts with explanations.
        - **Asset Comparison** — side-by-side tables for both assets and the optimal blend.
        - **Portfolio Interpretation** — a plain-English summary of what your results mean.

    ---

    ### Key concepts

    | Term | Meaning |
    |------|---------|
    | **Efficient Frontier** | The set of portfolios that offer the highest return for a given level of risk |
    | **Tangency Portfolio** | The portfolio with the highest Sharpe Ratio (best risk-adjusted return) |
    | **Sharpe Ratio** | Return above the risk-free rate per unit of risk |
    | **ESG Score** | A 0–100 measure of environmental, social, and governance quality |
    | **Optimal Portfolio** | The portfolio that maximises *your* utility, balancing return, risk, and ESG |
    | **CML** | Capital Market Line – the line from the risk-free rate through the tangency portfolio |

    ---

    ### ESG Minimum Constraint

    The **ESG Minimum Constraint** is an optional filter found in the sidebar under
    *🛡️ ESG Minimum Constraint*. When enabled, it excludes any portfolio whose weighted
    ESG score falls below the floor you set.

    **How to use it:**
    1. Toggle **Enable ESG Minimum** to ON in the sidebar.
    2. Use the slider to set your minimum portfolio ESG score (0–100).
    3. All results — optimal weights, metrics, charts, and tables — instantly update to
       reflect only portfolios that meet your floor.

    **What changes when it's active:**
    - The **Tangency Portfolio** shifts to the best risk-adjusted blend that still meets
      your ESG floor (may differ from the unconstrained tangency point).
    - The **Optimal Portfolio** is selected only from compliant blends.
    - On the **ESG-Efficient Frontier chart**, excluded portfolios appear as grey dots so
      you can see exactly which blends were ruled out.
    - On the **ESG vs MV Frontier chart**, the green constrained curve uses your floor
      instead of the default midpoint.
    - A warning banner appears on every results tab confirming the constraint is active.

    **When to use it:**
    - You have a firm sustainability policy (e.g. "no portfolio below ESG 60").
    - You want to see how much return you give up by enforcing a stricter ESG standard.
    - You are comparing a constrained vs unconstrained strategy side by side.

    ---

    ### 🛡️ ESG Minimum Constraint

    The **ESG Minimum Constraint** is an optional filter in the sidebar under
    *🛡️ ESG Minimum Constraint*. When enabled, it excludes any portfolio whose weighted
    ESG score falls below the floor you set.

    **How to use it:**
    1. Toggle **Enable ESG Minimum** to ON in the sidebar.
    2. Use the slider to set your minimum portfolio ESG score (0–100).
    3. All results — optimal weights, metrics, charts, and tables — update instantly to
       reflect only portfolios that meet your floor.

    **What changes when it is active:**
    - The **Tangency Portfolio** shifts to the best risk-adjusted blend that still meets
      your ESG floor (may differ from the unconstrained tangency point).
    - The **Optimal Portfolio** is chosen only from ESG-compliant blends.
    - On the **ESG-Efficient Frontier chart**, excluded portfolios appear as grey dots so
      you can clearly see which blends were ruled out.
    - On the **ESG vs MV Frontier chart**, the green constrained curve uses your floor
      instead of the default midpoint threshold.
    - A warning banner appears on every results tab confirming the constraint is active.

    **When to use it:**
    - You have a firm sustainability policy (e.g. "no portfolio below ESG 60").
    - You want to quantify how much return you sacrifice by enforcing a stricter ESG floor.
    - You are comparing a constrained vs unconstrained strategy side by side.

    ---

    ### Tips
    - Try adjusting the correlation between assets to see how diversification affects the frontier.
    - A negative correlation (e.g. –0.3) typically shrinks the minimum-variance point significantly.
    - If both assets have similar ESG scores, the ESG constraint will have little visible effect on
      the frontier comparison chart.
    """)

# ─────────────────────────────────────────────────────────────────────
# TAB 2 – Investor Profile & Results
# ─────────────────────────────────────────────────────────────────────
with tab2:
    # ESG floor notice
    if esg_min_active:
        st.warning(f"🛡️ **ESG Minimum Constraint is active** — only portfolios with a weighted ESG score ≥ **{esg_min_floor:.1f}** are considered. Results below reflect this restriction.")

    # Profile cards
    st.subheader("Your Investor Profile")
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**ESG Profile:** {esg_profile}  \n**ESG Score:** {total_esg_score}/30  \n{esg_description}")
    with col2:
        st.info(f"**Risk Profile:** {risk_profile}  \n**Risk Score:** {total_risk_score}/30  \n{risk_description}")

    st.markdown("---")

    # Optimal portfolio metrics
    st.subheader("📈 Optimal Portfolio Results")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Expected Return",  f"{ret_optimal*100:.2f}%")
    m2.metric("Portfolio Risk",   f"{sd_optimal*100:.2f}%")
    m3.metric("Sharpe Ratio",     f"{sharpe_optimal:.3f}")
    m4.metric("ESG Score",        f"{esg_optimal:.1f}")
    m5.metric("Investor Utility", f"{utility_optimal:.4f}")

    st.markdown("---")

    # Portfolio weights
    st.subheader("Portfolio Weights")
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
        st.info("""
        **📌 About this chart – ESG-Efficient Frontier: Risk vs Return**

        This chart maps every possible blend of your two assets onto a risk/return plane.
        Each dot represents a different portfolio, colour-coded from **red (low ESG)** to
        **green (high ESG)** based on its weighted ESG score.

        - The **grey dashed line (CML)** is the Capital Market Line — it passes through the
          risk-free rate and the tangency portfolio, showing the best risk/return trade-off
          available by combining the risky portfolio with cash.
        - The **gold diamond** marks the **Tangency Portfolio** — the risky-asset blend with
          the highest Sharpe Ratio (best reward per unit of risk), ignoring ESG preferences.
        - The **green triangle** marks the **Max ESG Portfolio** — the blend with the highest
          combined ESG score, regardless of financial performance.
        - The **red star** is **your Optimal Portfolio** — the point that maximises *your*
          personal utility function, which weighs return, risk tolerance, and ESG preference
          based on your questionnaire answers. This is the portfolio recommended for you.

        **Why it matters:** It shows you where your personalised recommendation sits on the
        frontier and whether you are trading financial return for sustainability — or whether
        the two align.
        """)

    with exp_col2:
        floor_note = f"Your **ESG Minimum of {esg_min_floor:.1f}** is active, so the green curve shows only portfolios meeting your floor." if esg_min_active else f"The midpoint threshold of **{esg_threshold:.0f}** (average of your two asset ESG scores) is used as the default floor."
        st.info(f"""
        **📌 About this chart – ESG-Efficient Frontier vs Mean-Variance Frontier**

        This chart overlays two separate efficient frontiers so you can see the impact of
        applying an ESG constraint to your portfolio.

        - The **blue curve** is the **unconstrained Mean-Variance Frontier** — the full range
          of risk/return trade-offs using any blend of the two assets.
        - The **green curve** is the **ESG-Constrained Frontier** — {floor_note}
        - Each frontier has its own **tangency portfolio (diamond)** and **Capital Market Line
          (dashed)**, representing the best risk-adjusted return available under each set of
          constraints.

        **Why it matters:** If the green (ESG) frontier sits noticeably *below* the blue
        (unconstrained) frontier, it means imposing an ESG floor comes at a financial cost.
        If the two curves largely overlap, then sustainable investing does **not** meaningfully
        reduce your risk-adjusted returns — a key argument in the ESG investing debate.
        The gap between the two tangency points quantifies the price of sustainability.
        """)

# ─────────────────────────────────────────────────────────────────────
# TAB 4 – Asset Comparison
# ─────────────────────────────────────────────────────────────────────
with tab4:
    if esg_min_active:
        st.warning(f"🛡️ **ESG Minimum active ({esg_min_floor:.1f})** — optimal weights and metrics reflect the ESG floor constraint.")
    st.subheader("📋 Asset Comparison")

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
    st.subheader("📋 Asset Outcomes Comparison")
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
    st.subheader("🔍 Portfolio Interpretation")
    if esg_min_active:
        st.warning(f"🛡️ **ESG Minimum active ({esg_min_floor:.1f})** — the interpretation below accounts for the ESG floor constraint.")

    st.markdown(f"""
The recommended portfolio reflects your selected risk tolerance and sustainability preferences.
Based on your questionnaire responses (**{risk_profile} risk profile**, **{esg_profile}**),
the model maximises a utility function that balances expected return, portfolio risk, and ESG impact.

- The portfolio delivers an **expected return of {ret_optimal*100:.2f}%** with a **volatility of {sd_optimal*100:.2f}%**.
- The **Sharpe Ratio of {sharpe_optimal:.3f}** reflects the risk-adjusted financial performance.
- When ESG preferences are incorporated, the **ESG-adjusted Sharpe Ratio is {sharpe_esg:.3f}**, reflecting sustainability-adjusted performance.
- The **portfolio ESG score is {esg_optimal:.2f}**, corresponding to a **{esg_level.lower()}**.
- Relative to the maximum Sharpe portfolio, you sacrifice **{-delta_ret*100:.2f}% of expected return**
  in exchange for an **ESG improvement of {delta_esg:.2f} points**.

Overall, the allocation balances financial performance with sustainability preferences in line
with your questionnaire responses.
    """)

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

st.markdown("---")
st.caption("EcoFolio – ESG Portfolio Optimiser | Built with Streamlit & NumPy")
