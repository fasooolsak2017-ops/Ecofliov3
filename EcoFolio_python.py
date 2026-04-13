import numpy as np
import matplotlib.pyplot as plt

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
# Safe input helpers
# ------------------------------
def get_float(prompt, low=None, high=None, scale=1):
    """Keep asking until the user enters a valid number within range."""
    while True:
        try:
            value = float(input(prompt))
            if low is not None and value < low:
                print(f"  ⚠  Value must be at least {low}. Try again.")
                continue
            if high is not None and value > high:
                print(f"  ⚠  Value must be at most {high}. Try again.")
                continue
            return value / scale
        except ValueError:
            print("  ⚠  Invalid input. Please enter a number.")

def get_int(prompt, low=None, high=None):
    """Keep asking until the user enters a valid integer within range."""
    while True:
        try:
            value = int(input(prompt))
            if low is not None and value < low:
                print(f"  ⚠  Value must be at least {low}. Try again.")
                continue
            if high is not None and value > high:
                print(f"  ⚠  Value must be at most {high}. Try again.")
                continue
            return value
        except ValueError:
            print("  ⚠  Invalid input. Please enter a whole number.")

def get_yes_no(prompt):
    """Keep asking until user enters y or n."""
    while True:
        answer = input(prompt).strip().lower()
        if answer in ("y", "yes"):
            return True
        elif answer in ("n", "no"):
            return False
        else:
            print("  ⚠  Please enter y or n.")

# ------------------------------
# User inputs
# ------------------------------
asset1_name = input("Asset 1 Name [e.g., Tech ETF]: ").strip()
if not asset1_name:
    asset1_name = "Asset 1"

r_h  = get_float(f"{asset1_name} Expected Return (%) [e.g., 5]: ", scale=100)
sd_h = get_float(f"{asset1_name} Standard Deviation (%) [e.g., 9]: ", low=0.01, scale=100)
esg_h = get_float(f"{asset1_name} ESG Score [e.g., 60]: ", low=0, high=100)

asset2_name = input("Asset 2 Name [e.g., Green Bond]: ").strip()
if not asset2_name:
    asset2_name = "Asset 2"

r_f  = get_float(f"{asset2_name} Expected Return (%) [e.g., 12]: ", scale=100)
sd_f = get_float(f"{asset2_name} Standard Deviation (%) [e.g., 20]: ", low=0.01, scale=100)
esg_f = get_float(f"{asset2_name} ESG Score [e.g., 60]: ", low=0, high=100)

rho_hf = get_float("Correlation between assets [-1 to 1, e.g., -0.2]: ", low=-1, high=1)
r_free = get_float("Risk-Free Rate (%) [e.g., 2]: ", scale=100)

# ------------------------------
# ESG Minimum Constraint
# ------------------------------
print("\n=== ESG Minimum Constraint ===")
esg_min_active = get_yes_no("Do you want to apply a minimum ESG score constraint? (y/n): ")

if esg_min_active:
    esg_min_floor = get_float(
        "Enter the minimum portfolio ESG score (0-100) [e.g., 50]: ",
        low=0, high=100
    )
    print(f"  ✅ ESG minimum constraint active — portfolios with ESG score < {esg_min_floor:.1f} will be excluded.")
else:
    esg_min_floor = 0.0
    print("  ESG minimum constraint is OFF — all portfolios are eligible.")

# ------------------------------
# ESG Questionnaire
# ------------------------------
print("\n=== ESG Questionnaire ===")
print("Please rate each statement from 1 to 10.")
print("1 = not important at all, 10 = extremely important")

env_score = get_int(
    "\n1. How important is environmental sustainability "
    "(e.g. carbon reduction, pollution control, resource efficiency) "
    "when making your investment decisions, even if it reduces your returns? ",
    low=1, high=10)

social_score = get_int(
    "\n2. How important are social factors "
    "(e.g. labour practices, diversity, community impact) "
    "when making your investment decisions, even if it reduces your returns? ",
    low=1, high=10)

gov_score = get_int(
    "\n3. How important is strong corporate governance "
    "(e.g. transparency, accountability, ethical leadership) "
    "when making your investment decisions, even if it reduces your returns? ",
    low=1, high=10)

total_esg_score = env_score + social_score + gov_score

if total_esg_score <= 8:
    esg_profile = "Traditional Investor"
    esg_description = (
        "ESG factors are not a primary consideration in your investment decisions. "
        "Your approach focuses mainly on financial performance, with limited emphasis "
        "on environmental, social, or governance aspects."
    )
elif total_esg_score <= 14:
    esg_profile = "ESG Aware Investor"
    esg_description = (
        "ESG factors are considered in your investment decisions, particularly in "
        "identifying and avoiding potential risks. However, they are not a central "
        "driver of your overall investment strategy."
    )
elif total_esg_score <= 20:
    esg_profile = "Balanced Investor"
    esg_description = (
        "ESG factors play a meaningful role in your investment approach alongside "
        "financial considerations. You aim to balance performance objectives with "
        "an interest in sustainability."
    )
elif total_esg_score <= 26:
    esg_profile = "Strong ESG Preference Investor"
    esg_description = (
        "ESG considerations are an important part of your investment decisions. "
        "You tend to favour investments with stronger sustainability characteristics, "
        "while still considering financial outcomes."
    )
else:
    esg_profile = "ESG-Focused Investor"
    esg_description = (
        "ESG outcomes are a central component of your investment approach. "
        "Your decisions place significant weight on environmental and social impact, "
        "alongside financial considerations."
    )

print("\n--- ESG Results ---")
print(f"Total ESG Score: {total_esg_score} / 30")
print(f"ESG Profile: {esg_profile}")
lambda_esg = esg_profile_map[esg_profile]
print(esg_description)


# ------------------------------
# Risk Questionnaire
# ------------------------------
print("\n=== Risk Profile Questionnaire ===")
print("Please answer each question using a score from 1 to 10.")
print("1 means you lean fully towards the statement on the left.")
print("10 means you lean fully towards the statement on the right.")

print("\n1. If your investment fell by 10% in a short period, how would you react?")
print("1 = Sell immediately to avoid further losses")
print("10 = Hold or invest more to take advantage of lower prices")
q1 = get_int("Your answer (1-10): ", low=1, high=10)

print("\n2. Which matters more to you when investing?")
print("1 = Minimise risk and protect capital")
print("10 = Maximise return even with higher risk")
q2 = get_int("Your answer (1-10): ", low=1, high=10)

print("\n3. How comfortable are you with investments that experience significant price fluctuations?")
print("1 = Very uncomfortable")
print("10 = Very comfortable")
q3 = get_int("Your answer (1-10): ", low=1, high=10)

total_risk_score = q1 + q2 + q3

if total_risk_score <= 8:
    risk_profile = "Cautious"
    risk_description = (
        "You place strong importance on stability and are less comfortable with large investment losses."
    )
elif total_risk_score <= 14:
    risk_profile = "Conservative"
    risk_description = (
        "You are willing to take some risk, but protecting your capital remains a higher priority."
    )
elif total_risk_score <= 20:
    risk_profile = "Balanced"
    risk_description = (
        "You seek a middle ground between stability and growth, accepting some volatility for better returns."
    )
elif total_risk_score <= 26:
    risk_profile = "Assertive"
    risk_description = (
        "You are comfortable taking on more risk in pursuit of stronger long term growth."
    )
else:
    risk_profile = "Aggressive"
    risk_description = (
        "You are highly comfortable with market fluctuations and prioritise maximising returns over short term stability."
    )

print("\n--- Risk Results ---")
print(f"Total Risk Score: {total_risk_score} / 30")
print(f"Risk Profile: {risk_profile}")
gamma_risk = risk_profile_map[risk_profile]
print(risk_description)

# ------------------------------
# Functions
# ------------------------------
def portfolio_ret(w1, r1, r2):
    return w1 * r1 + (1 - w1) * r2

def portfolio_sd(w1, sd1, sd2, rho):
    return np.sqrt(w1**2 * sd1**2 + (1-w1)**2 * sd2**2 + 2 * rho * w1 * (1-w1) * sd1 * sd2)

# -----------------------------------------------
# Pedersen et al. (2021) direct optimisation
# max  x'μ − (γ/2) x'Σx + λ · s̄
# s̄ = (x1·s1 + x2·s2) / (x1+x2)
# x1,x2 >= 0,  x1+x2 <= 1  (no leverage)
# -----------------------------------------------
from scipy.optimize import minimize as _minimize

_cov12 = rho_hf * sd_h * sd_f
_Sigma = np.array([[sd_h**2, _cov12], [_cov12, sd_f**2]])
_mu    = np.array([r_h, r_f])
_esg_v = np.array([esg_h, esg_f])

def _neg_obj(x):
    x1, x2 = x
    total = x1 + x2
    if total <= 1e-10:
        # all in risk-free
        return -(r_free)
    x_rf  = 1.0 - x1 - x2
    s_bar = (x1*(_esg_v[0]/100) + x2*(_esg_v[1]/100)) / total
    # full portfolio return including risk-free
    xT_mu    = x1*_mu[0] + x2*_mu[1] + x_rf*r_free
    xT_Sig_x = x1**2*_Sigma[0,0] + x2**2*_Sigma[1,1] + 2*x1*x2*_Sigma[0,1]
    return -(xT_mu - (gamma_risk/2)*xT_Sig_x + lambda_esg*s_bar)

_bounds = [(0.0, 1.0), (0.0, 1.0)]
_constraints = [{'type': 'ineq', 'fun': lambda x: 1.0 - x[0] - x[1]}]
if esg_min_active:
    _constraints.append({
        'type': 'ineq',
        'fun': lambda x: (esg_h - esg_min_floor)*x[0] + (esg_f - esg_min_floor)*x[1]
    })

_starts = [(0.5,0.5),(0.3,0.3),(0.1,0.1),(0.4,0.4),(0.25,0.25),
           (0.2,0.6),(0.6,0.2),(0.1,0.8),(0.8,0.1),(0.0,0.5),(0.5,0.0)]
_best_val = -np.inf
_best_x   = np.array([0.0, 0.0])
for _x0 in _starts:
    _res = _minimize(_neg_obj, _x0, method='SLSQP',
                     bounds=_bounds, constraints=_constraints,
                     options={'ftol': 1e-14, 'maxiter': 10000})
    if -_res.fun > _best_val:
        _best_val = -_res.fun
        _best_x   = _res.x

x1_optimal = float(np.clip(_best_x[0], 0.0, 1.0))
x2_optimal = float(np.clip(_best_x[1], 0.0, 1.0))
if x1_optimal + x2_optimal > 1.0:
    _s = 1.0 / (x1_optimal + x2_optimal)
    x1_optimal *= _s; x2_optimal *= _s

w1_optimal   = x1_optimal
w2_optimal   = x2_optimal
w_rf_optimal = 1.0 - w1_optimal - w2_optimal

ret_optimal  = r_free + w1_optimal*(r_h-r_free) + w2_optimal*(r_f-r_free)
_x_vec       = np.array([w1_optimal, w2_optimal])
_var_opt     = float(_x_vec @ _Sigma @ _x_vec)
sd_optimal   = float(np.sqrt(_var_opt)) if _var_opt > 0 else 0.0
_rt          = w1_optimal + w2_optimal
esg_optimal  = ((w1_optimal*esg_h + w2_optimal*esg_f) / _rt) if _rt > 1e-10 else 0.0
utility_optimal = _best_val

# Tangency portfolio (chart reference)
_wt = np.linspace(0, 1, 1000)
_sh = []
for _w in _wt:
    _rt2 = _w*r_h + (1-_w)*r_f
    _sd2 = np.sqrt(_w**2*sd_h**2 + (1-_w)**2*sd_f**2 + 2*_w*(1-_w)*rho_hf*sd_h*sd_f)
    _e   = _w*esg_h + (1-_w)*esg_f
    if esg_min_active and _e < esg_min_floor:
        _sh.append(-np.inf)
    else:
        _sh.append((_rt2-r_free)/_sd2 if _sd2 > 0 else -np.inf)
_ti = int(np.argmax(_sh))
w1_tangency  = float(_wt[_ti]); w2_tangency = 1.0 - w1_tangency
ret_tangency = w1_tangency*r_h + w2_tangency*r_f
sd_tangency  = float(np.sqrt(w1_tangency**2*sd_h**2 + w2_tangency**2*sd_f**2
                              + 2*w1_tangency*w2_tangency*rho_hf*sd_h*sd_f))
esg_tangency = w1_tangency*esg_h + w2_tangency*esg_f
delta_ret    = ret_tangency - ret_optimal
delta_esg    = esg_optimal - esg_tangency

# Derived metrics
pri_score      = esg_optimal
sharpe_optimal = (ret_optimal - r_free) / sd_optimal if sd_optimal > 0 else 0
sharpe_esg     = (ret_optimal + lambda_esg*(esg_optimal/100) - r_free) / sd_optimal if sd_optimal > 0 else 0

if esg_optimal >= 70:
    esg_level = "High ESG Impact"
elif esg_optimal >= 40:
    esg_level = "Medium ESG Impact"
else:
    esg_level = "Low ESG Impact"

is_corner = (w1_optimal < 1e-4 or w2_optimal < 1e-4) and (w1_optimal + w2_optimal > 1e-4)

# ------------------------------
# Display Results
# ------------------------------
print("\n==============================")
print("ESG-AWARE OPTIMAL PORTFOLIO")
if esg_min_active:
    print(f"  [ESG Minimum Constraint: >= {esg_min_floor:.1f}]")
print("==============================")

if is_corner:
    low  = asset1_name if w1_optimal < 1e-4 else asset2_name
    high = asset2_name if w1_optimal < 1e-4 else asset1_name
    print(f"\n  📐 CORNER SOLUTION: x({low})=0 — at λ={lambda_esg:.2f}, holding {low} is not optimal.")
    print(f"     The non-negativity constraint on {low} is binding. This is economically meaningful.")

print("\nPortfolio Weights")
print(f"Risk-Free Asset Weight: {w_rf_optimal*100:.2f}%")
print(f"{asset1_name} Weight: {w1_optimal*100:.2f}%")
print(f"{asset2_name} Weight: {w2_optimal*100:.2f}%")

print("\nFinancial Performance")
print(f"Investor Utility Score: {utility_optimal:.4f}")
print(f"Expected Return: {ret_optimal*100:.2f}%")
print(f"Portfolio Risk (Std Dev): {sd_optimal*100:.2f}%")
print(f"Sharpe Ratio: {sharpe_optimal:.3f}")
print(f"ESG-adjusted Sharpe Ratio: {sharpe_esg:.3f}")

print("\nSustainability Metrics")
print(f"Portfolio ESG Score: {esg_optimal:.2f}")
print(f"PRI Score: {pri_score:.2f}")
print(f"Impact Level: {esg_level}")

print("\nReturn vs Sustainability Trade-off")
print(f"Return difference vs tangency: {-delta_ret*100:.2f}%")
print(f"ESG improvement vs tangency: {delta_esg:.2f} points")

# ------------------------------
# Interpretation
# ------------------------------
print("\nPortfolio Interpretation")
print("------------------------------")
print(
    "The recommended portfolio reflects your selected risk tolerance "
    "and sustainability preferences."
)
if esg_min_active:
    print(
        f"Note: An ESG minimum constraint of {esg_min_floor:.1f} was applied — "
        "only portfolios meeting this floor were considered."
    )
print(
    f"Based on your preferences, the model maximises a utility function "
    "that balances expected return, portfolio risk, and ESG impact."
)
print(
    f"The portfolio delivers an expected return of {ret_optimal*100:.2f}% "
    f"with a volatility of {sd_optimal*100:.2f}%."
)
print(
    f"The Sharpe ratio of {sharpe_optimal:.2f} indicates the "
    "risk-adjusted financial performance of the portfolio."
)
print(
    f"When ESG preferences are incorporated, the ESG-adjusted Sharpe ratio "
    f"is {sharpe_esg:.2f}, reflecting sustainability-adjusted performance."
)
print(
    f"The portfolio ESG score is {esg_optimal:.2f}, "
    f"corresponding to a {esg_level.lower()}."
)
print(
    f"This produces a PRI score of {pri_score:.2f}, "
    "indicating the overall sustainability alignment of the portfolio."
)
print(
    f"Relative to the maximum Sharpe ratio portfolio, you sacrifice "
    f"{-delta_ret*100:.2f}% of expected return in exchange for "
    f"an ESG improvement of {delta_esg:.2f} points."
)
print(
    "Overall, the allocation balances financial performance "
    "with sustainability preferences in line with your questionnaire responses."
)

# ------------------------------
# Asset Comparison Table
# ------------------------------
sharpe_h = (r_h - r_free) / sd_h if sd_h > 0 else 0
sharpe_f = (r_f - r_free) / sd_f if sd_f > 0 else 0

col_w   = 28
a1_w    = max(len(asset1_name), 18)
a2_w    = max(len(asset2_name), 18)
total_w = col_w + a1_w + a2_w + 4

print("\n" + "=" * total_w)
print("ASSET COMPARISON TABLE")
print("=" * total_w)
print(f"{'Metric':<{col_w}} {asset1_name:>{a1_w}}   {asset2_name:>{a2_w}}")
print("-" * total_w)
print(f"{'Expected Return (%)':<{col_w}} {r_h*100:>{a1_w}.2f}   {r_f*100:>{a2_w}.2f}")
print(f"{'Standard Deviation (%)':<{col_w}} {sd_h*100:>{a1_w}.2f}   {sd_f*100:>{a2_w}.2f}")
print(f"{'ESG Score':<{col_w}} {esg_h:>{a1_w}.2f}   {esg_f:>{a2_w}.2f}")
print(f"{'Individual Sharpe Ratio':<{col_w}} {sharpe_h:>{a1_w}.3f}   {sharpe_f:>{a2_w}.3f}")
print(f"{'Tangency Weight (%)':<{col_w}} {w1_tangency*100:>{a1_w}.2f}   {w2_tangency*100:>{a2_w}.2f}")
print(f"{'Optimal Portfolio Weight (%)':<{col_w}} {w1_optimal*100:>{a1_w}.2f}   {w2_optimal*100:>{a2_w}.2f}")
print("=" * total_w)

better_ret  = asset1_name if r_h   > r_f   else asset2_name
better_risk = asset1_name if sd_h  < sd_f  else asset2_name
better_esg  = asset1_name if esg_h > esg_f else asset2_name
better_sr   = asset1_name if sharpe_h > sharpe_f else asset2_name

print("\nAt-a-glance winner per metric:")
print(f"  Higher Return       → {better_ret}")
print(f"  Lower Volatility    → {better_risk}")
print(f"  Higher ESG Score    → {better_esg}")
print(f"  Higher Sharpe Ratio → {better_sr}")

# ------------------------------
# Asset Outcomes Comparison Table
# ------------------------------
standalone_ret_1   = r_free + 1.0 * (r_h - r_free)
standalone_sd_1    = sd_h
standalone_esg_1   = esg_h
standalone_util_1  = standalone_ret_1 - 0.5 * gamma_risk * standalone_sd_1**2 + lambda_esg * (standalone_esg_1 / 100)
standalone_sharpe_1 = (standalone_ret_1 - r_free) / standalone_sd_1 if standalone_sd_1 > 0 else 0
standalone_esg_sharpe_1 = (standalone_ret_1 + lambda_esg * (standalone_esg_1 / 100) - r_free) / standalone_sd_1 if standalone_sd_1 > 0 else 0
standalone_ret_per_risk_1 = standalone_ret_1 / standalone_sd_1 if standalone_sd_1 > 0 else 0

standalone_ret_2   = r_free + 1.0 * (r_f - r_free)
standalone_sd_2    = sd_f
standalone_esg_2   = esg_f
standalone_util_2  = standalone_ret_2 - 0.5 * gamma_risk * standalone_sd_2**2 + lambda_esg * (standalone_esg_2 / 100)
standalone_sharpe_2 = (standalone_ret_2 - r_free) / standalone_sd_2 if standalone_sd_2 > 0 else 0
standalone_esg_sharpe_2 = (standalone_ret_2 + lambda_esg * (standalone_esg_2 / 100) - r_free) / standalone_sd_2 if standalone_sd_2 > 0 else 0
standalone_ret_per_risk_2 = standalone_ret_2 / standalone_sd_2 if standalone_sd_2 > 0 else 0

opt_label = "Optimal Blend"
oc_w    = 32
o1_w    = max(len(asset1_name), 16)
o2_w    = max(len(asset2_name), 16)
ob_w    = max(len(opt_label), 16)
oc_total = oc_w + o1_w + o2_w + ob_w + 6

print("\n" + "=" * oc_total)
print("ASSET OUTCOMES COMPARISON")
print("(Hypothetical 100% allocation to each asset vs Optimal Portfolio)")
print("=" * oc_total)
print(f"{'Metric':<{oc_w}} {asset1_name:>{o1_w}}   {asset2_name:>{o2_w}}   {opt_label:>{ob_w}}")
print("-" * oc_total)
print(f"{'Expected Return (%)':<{oc_w}} {standalone_ret_1*100:>{o1_w}.2f}   {standalone_ret_2*100:>{o2_w}.2f}   {ret_optimal*100:>{ob_w}.2f}")
print(f"{'Portfolio Risk / Std Dev (%)':<{oc_w}} {standalone_sd_1*100:>{o1_w}.2f}   {standalone_sd_2*100:>{o2_w}.2f}   {sd_optimal*100:>{ob_w}.2f}")
print(f"{'Sharpe Ratio':<{oc_w}} {standalone_sharpe_1:>{o1_w}.3f}   {standalone_sharpe_2:>{o2_w}.3f}   {sharpe_optimal:>{ob_w}.3f}")
print(f"{'ESG Score':<{oc_w}} {standalone_esg_1:>{o1_w}.2f}   {standalone_esg_2:>{o2_w}.2f}   {esg_optimal:>{ob_w}.2f}")
print(f"{'ESG-Adjusted Sharpe Ratio':<{oc_w}} {standalone_esg_sharpe_1:>{o1_w}.3f}   {standalone_esg_sharpe_2:>{o2_w}.3f}   {sharpe_esg:>{ob_w}.3f}")
print(f"{'Return per Unit of Risk':<{oc_w}} {standalone_ret_per_risk_1:>{o1_w}.3f}   {standalone_ret_per_risk_2:>{o2_w}.3f}   {(ret_optimal/sd_optimal if sd_optimal > 0 else 0):>{ob_w}.3f}")
print(f"{'Investor Utility Score':<{oc_w}} {standalone_util_1:>{o1_w}.4f}   {standalone_util_2:>{o2_w}.4f}   {utility_optimal:>{ob_w}.4f}")
print("=" * oc_total)

diff_ret  = (standalone_ret_1 - standalone_ret_2) * 100
diff_sd   = (standalone_sd_1 - standalone_sd_2) * 100
diff_esg  = standalone_esg_1 - standalone_esg_2
diff_util = standalone_util_1 - standalone_util_2

print(f"\nDifferences ({asset1_name} minus {asset2_name}):")
print(f"  Return gap:          {diff_ret:+.2f} pp")
print(f"  Risk gap:            {diff_sd:+.2f} pp")
print(f"  ESG gap:             {diff_esg:+.2f} points")
print(f"  Utility gap:         {diff_util:+.4f}")

if utility_optimal >= standalone_util_1 and utility_optimal >= standalone_util_2:
    print(f"\n  ✅ The Optimal Blend outperforms both standalone assets on utility.")
elif utility_optimal >= standalone_util_1:
    print(f"\n  ✅ The Optimal Blend outperforms {asset1_name} on utility.")
    print(f"  ⚠  {asset2_name} standalone has higher utility — consider ESG / risk trade-offs.")
elif utility_optimal >= standalone_util_2:
    print(f"\n  ✅ The Optimal Blend outperforms {asset2_name} on utility.")
    print(f"  ⚠  {asset1_name} standalone has higher utility — consider ESG / risk trade-offs.")
else:
    print(f"\n  ⚠  Both standalone assets show higher raw utility — "
          "the blend adds diversification value.")

# ------------------------------
# Build the risky-asset frontier for plotting
# ------------------------------
frontier_weights = np.linspace(0, 1, 1000)
frontier_returns = []
frontier_risks   = []
frontier_esg     = []
frontier_valid   = []  # True if blend passes ESG floor (or floor is off)

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

# ------------------------------
# Plot: ESG-Efficient Frontier
# ------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6.5))

# ── LEFT PANEL: ESG-Efficient Frontier ──
if esg_min_active:
    # Greyed-out excluded portfolios
    ax1.scatter(frontier_risks[~frontier_valid], frontier_returns[~frontier_valid],
                color="lightgrey", s=6, zorder=1, alpha=0.35,
                label=f"Excluded (ESG < {esg_min_floor:.0f})")
    # Colour-coded valid portfolios
    sc = ax1.scatter(frontier_risks[frontier_valid], frontier_returns[frontier_valid],
                     c=frontier_esg[frontier_valid], cmap="RdYlGn", s=8, zorder=2,
                     alpha=0.85, label=f"Frontier (ESG >= {esg_min_floor:.0f})",
                     vmin=frontier_esg.min(), vmax=frontier_esg.max())
    cbar = fig.colorbar(sc, ax=ax1, pad=0.02)
else:
    sc = ax1.scatter(frontier_risks, frontier_returns, c=frontier_esg,
                     cmap="RdYlGn", s=8, zorder=2, label="Frontier portfolios")
    cbar = fig.colorbar(sc, ax=ax1, pad=0.02)
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
            label=f"Optimal (w$_1$={w1_optimal*100:.1f}%)")

ax1.set_xlabel("Portfolio Std Dev (%)", fontsize=11)
ax1.set_ylabel("Expected Return (%)", fontsize=11)
title1 = "ESG-Efficient Frontier: Risk vs Return"
if esg_min_active:
    title1 += f"\n[ESG Minimum: {esg_min_floor:.1f}]"
ax1.set_title(title1, fontsize=13, fontweight="bold")
ax1.legend(loc="upper left", fontsize=7.5, framealpha=0.9)
ax1.grid(True, alpha=0.3)

# ── RIGHT PANEL: ESG Frontier vs Mean-Variance Frontier ──
# Use user-set floor if active, else default midpoint
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
    floor_label = "your floor" if esg_min_active else "default midpoint"
    ax2.plot(con_risks, con_returns,
             color="seagreen", linewidth=2.5,
             label=f"Mean-Variance Frontier (ESG >= {esg_threshold:.0f} — {floor_label})")
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

filepath = "esg_frontier.png"
fig.savefig(filepath, dpi=150)
print(f"\n✅ Chart saved to: {filepath}")

plt.show()
