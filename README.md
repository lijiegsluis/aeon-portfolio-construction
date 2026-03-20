# Aeon Portfolio Construction

**Build a Mock Fund · P&L Attribution · Long/Short Exposure · Capital Simulation · Risk Budget Discipline**

*LiJie Guo · Aeon Nimbus Research · lijieguo.substack.com · [LinkedIn](https://www.linkedin.com/in/lijieguo-es/)*

---

## Overview

Portfolio construction is the competency that separates analysts from portfolio managers. Finding a well-supported idea is necessary but not sufficient — the PM's job is to determine how much capital to commit to that idea relative to every other position in the book, manage the resulting net and gross exposures, and attribute returns to understand whether the process is working as intended. This tool replicates that workflow end-to-end: position entry, P&L tracking, exposure decomposition, pre-trade capital simulation, and risk budget enforcement.

```bash
python main.py
```

Python 3.8 or later. No external dependencies.

---

## Modules

| Module | Function |
|--------|----------|
| Portfolio Builder | Enter positions with ticker, direction, entry, current price, and share count. Computes per-position P&L, market value, return contribution, and full exposure decomposition. |
| Capital Simulation | Pre-trade analysis: models expected gain, maximum loss, and reward-to-risk for each proposed position before capital is committed. |
| Risk Budget | Monitors remaining risk capacity relative to deployed positions and enforces concentration limits. |

---

## Methodology

### Long/Short P&L Mechanics

The direction of a position determines the sign convention for profit and loss. For a long, profit accrues as the price rises above the entry; for a short, profit accrues as it falls:

```
Long P&L  = (Current − Entry) × Shares
Short P&L = (Entry − Current) × Shares
```

Short exposure is often misunderstood: the market value of the short is the current cost to close the position, `Current × Shares`, while the original obligation was `Entry × Shares`. A rising price is a loss for the short holder — the liability has grown.

### Gross and Net Exposure

Exposure metrics are the language of professional risk monitoring. Two distinct measures must be tracked simultaneously:

```
Long Exposure  = Σ Market Value of all long positions
Short Exposure = Σ Market Value of all short positions
Gross Exposure = Long + Short      (total leverage deployed)
Net Exposure   = Long − Short      (aggregate directional bias)
Net %          = Net / Total Capital × 100
Gross %        = Gross / Total Capital × 100
```

Gross exposure drives realised portfolio volatility — it is the total capital at work, regardless of direction. Net exposure captures the residual directional beta to the market. A 130/30 fund carries 160% gross and 100% net; it is fully market-exposed in aggregate direction but uses embedded shorts to fund incremental long alpha and reduce single-stock risk. A market-neutral fund targets net exposure close to zero while maintaining high gross exposure — theoretically eliminating market beta while preserving stock-level alpha.

### P&L Attribution

Attribution answers the question every PM is asked in every review: which positions made money, by how much, and relative to what baseline? Each position's contribution is measured as its P&L relative to the total cost basis of the book:

```
Position Contribution % = Position P&L / |Total Cost Basis| × 100
```

Attribution is not merely retrospective. Patterns in attribution — consistent alpha from a particular sector, consistent drag from another — reveal whether the investment process is generating returns from the intended source or from accidental factor exposures. A PM who generates returns primarily from long positions in a rising market but attributes them to stock selection is accumulating hidden beta risk.

### Capital Simulation — Pre-Trade Analysis

Before committing capital, a structured pre-trade analysis models each position's expected economic outcomes:

```
Dollar Allocation  = Capital × Allocation %
Shares             = floor(Dollar Allocation / Entry Price)
Expected Gain      = Shares × |Target − Entry|
Maximum Loss       = Shares × |Entry − Stop|
R-Multiple         = Expected Gain / Maximum Loss
```

At the portfolio level, these aggregate into a prospective risk/reward profile before a single share is purchased. This discipline — modelling the expected P&L of a proposed book prior to execution — is standard practice at institutional long/short funds and prevents the common error of building a portfolio position by position without considering aggregate exposure.

### Risk Budget Discipline

Risk budgeting allocates the portfolio's total risk capacity across positions in proportion to their expected contribution to return — not their nominal dollar size. The practical rules enforced here reflect institutional standards:

- **Maximum single position size:** typically 8% of the portfolio, to prevent concentration from a single high-conviction name overwhelming the diversification benefits of the book
- **Maximum gross deployed:** typically 80–90%, preserving a cash buffer for opportunistic deployment and redemption risk management
- **Net exposure monitoring:** prevents inadvertent directional drift as positions are added over time

### Conviction Weighting

Uniform position sizing — equal weights across all holdings — is a common default that implicitly claims equal confidence in every idea. A more intellectually honest approach maps qualitative conviction to quantitative size modifiers:

- High conviction (8–10 / 10): size up to the maximum position limit
- Medium conviction (5–7 / 10): 60–80% of the position limit
- Low conviction (1–4 / 10): 40% or less, or pass and revisit the thesis

---

## Why This Matters

The craft of portfolio construction receives systematically less attention in analyst development than idea generation and financial modelling. Yet capital allocation — how much to put into each idea — frequently has a larger impact on returns than idea quality itself. A correctly sized mediocre idea outperforms a poorly sized excellent one; over-sizing a loss compounds drawdown; under-sizing a winner limits the compounding that creates long-term outperformance.

The gross/net framework matters because leverage and direction are separate risks that require separate monitoring. A portfolio with 200% gross exposure and 10% net exposure is highly levered but directionally neutral; its risk comes from stock-specific volatility, not market beta. Conflating the two — as unsophisticated exposure monitoring often does — leads to misclassification of the portfolio's actual risk profile.

P&L attribution closes the feedback loop. Without it, a portfolio manager cannot distinguish skill from luck, identify which ideas are systematically generating alpha, or diagnose whether the process is working. Attribution done monthly and reviewed quarterly is the professional standard for good reason: it converts investing from an intuitive art into a disciplined, empirically grounded practice.

---

## Example Output

```
════════════════════════════════════════════════════════════════
  AEON PORTFOLIO CONSTRUCTION — 3 POSITIONS
════════════════════════════════════════════════════════════════

  Ticker   Dir   Entry    Current   Shares   MV         P&L
  ─────────────────────────────────────────────────────────
  VNET     Long  $10.51   $14.30     500    $7,150    +$1,895  (+36.1%)
  MELI     Long  $2,161   $2,320      20   $46,400    +$3,180   (+7.4%)
  SPY      Short  $480     $461       50   $23,050      +$950   (+4.0%)
  ─────────────────────────────────────────────────────────

  Total Market Value     : $76,600
  Total Unrealised P&L   : +$6,025  (+8.8%)
  Long Exposure          : $53,550  (69.9%)
  Short Exposure         : $23,050  (30.1%)
  Net Exposure           : 39.9% net long
  Gross Exposure         : 99.9%

  Risk Check: Largest position MELI = 60.6% of book
  — exceeds 8% single-position cap (concentration risk, illustrative)

  P&L Attribution:
  VNET Long  : +36.1% return  →  contributes +2.48% to portfolio
  MELI Long  :  +7.4% return  →  contributes +4.15% to portfolio
  SPY  Short :  +4.0% return  →  contributes +1.24% to portfolio
```

---

*LiJie Guo · Aeon Nimbus Research · lijieguo.substack.com · [LinkedIn](https://www.linkedin.com/in/lijieguo-es/)*
