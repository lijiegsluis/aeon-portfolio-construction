"""
Aeon Portfolio Construction Tool
=================================
A standalone CLI tool for portfolio construction, capital simulation,
and risk budgeting. Uses Python standard library only.

Author: LiJie Guo
"""

import math
import statistics


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def fmt_currency(val: float, decimals: int = 2) -> str:
    sign = "-" if val < 0 else ""
    abs_val = abs(val)
    formatted = f"{abs_val:,.{decimals}f}"
    return f"{sign}${formatted}"


def fmt_pct(val: float, decimals: int = 2) -> str:
    return f"{val:+.{decimals}f}%"


def fmt_pct_plain(val: float, decimals: int = 2) -> str:
    return f"{val:.{decimals}f}%"


def divider(char: str = "-", width: int = 72) -> str:
    return char * width


def header(title: str, width: int = 72) -> str:
    pad = (width - len(title) - 2) // 2
    return f"\n{'=' * width}\n{' ' * pad} {title}\n{'=' * width}"


def prompt_float(msg: str) -> float:
    while True:
        try:
            return float(input(msg).strip())
        except ValueError:
            print("  [!] Please enter a valid number.")


def prompt_int(msg: str, min_val: int = 1) -> int:
    while True:
        try:
            val = int(input(msg).strip())
            if val < min_val:
                print(f"  [!] Value must be >= {min_val}.")
                continue
            return val
        except ValueError:
            print("  [!] Please enter a valid integer.")


def prompt_choice(msg: str, choices: list) -> str:
    choices_upper = [c.upper() for c in choices]
    while True:
        val = input(msg).strip().upper()
        if val in choices_upper:
            return val
        print(f"  [!] Please enter one of: {', '.join(choices)}.")


# ---------------------------------------------------------------------------
# Module 1: Portfolio Builder & P&L Attribution
# ---------------------------------------------------------------------------

def module_portfolio_builder(demo: bool = False):
    print(header("MODULE 1 — PORTFOLIO BUILDER & P&L ATTRIBUTION"))

    if demo:
        print("\n  [Demo mode] Loading 3 demo positions...\n")
        positions = [
            {"ticker": "VNET",  "direction": "LONG",  "entry": 10.51, "current": 10.51, "shares": 500},
            {"ticker": "MELI",  "direction": "LONG",  "entry": 2161.0, "current": 2161.0, "shares": 20},
            {"ticker": "SPY",   "direction": "SHORT", "entry": 480.0,  "current": 480.0,  "shares": 50},
        ]
    else:
        n = prompt_int("\n  Number of positions to enter: ")
        positions = []
        for i in range(n):
            print(f"\n  --- Position {i + 1} ---")
            ticker    = input("    Ticker: ").strip().upper()
            direction = prompt_choice("    Direction (Long/Short): ", ["Long", "Short"])
            entry     = prompt_float("    Entry price: $")
            current   = prompt_float("    Current price: $")
            shares    = prompt_int("    Shares: ", min_val=1)
            positions.append({
                "ticker":    ticker,
                "direction": direction,
                "entry":     entry,
                "current":   current,
                "shares":    shares,
            })

    # Per-position calculations
    results = []
    for p in positions:
        cost = p["entry"] * p["shares"]
        mv   = p["current"] * p["shares"]

        if p["direction"] == "LONG":
            pnl = (p["current"] - p["entry"]) * p["shares"]
        else:  # SHORT
            pnl = (p["entry"] - p["current"]) * p["shares"]

        ret_pct = (pnl / abs(cost) * 100) if cost != 0 else 0.0

        results.append({
            **p,
            "cost":    cost,
            "mv":      mv,
            "pnl":     pnl,
            "ret_pct": ret_pct,
        })

    # Portfolio-level aggregates
    total_cost    = sum(r["cost"] for r in results)
    total_mv      = sum(r["mv"] for r in results)
    total_pnl     = sum(r["pnl"] for r in results)
    port_ret_pct  = (total_pnl / abs(total_cost) * 100) if total_cost != 0 else 0.0

    long_mv  = sum(r["mv"] for r in results if r["direction"] == "LONG")
    short_mv = sum(r["mv"] for r in results if r["direction"] == "SHORT")

    gross_exp_pct = ((long_mv + short_mv) / total_mv * 100) if total_mv != 0 else 0.0
    net_exp_pct   = ((long_mv - short_mv) / total_mv * 100) if total_mv != 0 else 0.0

    # P&L attribution
    for r in results:
        r["pnl_contrib_pct"] = (r["pnl"] / abs(total_cost) * 100) if total_cost != 0 else 0.0

    # Risk check
    for r in results:
        r["wt_pct"] = (r["mv"] / total_mv * 100) if total_mv != 0 else 0.0

    # --- Print position table ---
    print(f"\n{divider()}")
    col = "{:<6}  {:>5}  {:>10}  {:>10}  {:>8}  {:>12}  {:>10}  {:>8}  {:>9}"
    print(col.format(
        "TICKER", "DIR", "ENTRY", "CURRENT", "SHARES",
        "MKT VALUE", "P&L", "RET%", "CONTRIB%"
    ))
    print(divider())

    for r in results:
        print(col.format(
            r["ticker"],
            r["direction"][:5],
            f"${r['entry']:,.2f}",
            f"${r['current']:,.2f}",
            f"{r['shares']:,}",
            fmt_currency(r["mv"]),
            fmt_currency(r["pnl"]),
            f"{r['ret_pct']:+.2f}%",
            f"{r['pnl_contrib_pct']:+.2f}%",
        ))

    print(divider())

    # --- Portfolio summary ---
    print(f"\n  {'PORTFOLIO SUMMARY':}")
    print(f"  {'Total Market Value':30s}  {fmt_currency(total_mv)}")
    print(f"  {'Total Cost Basis':30s}  {fmt_currency(total_cost)}")
    print(f"  {'Total Unrealized P&L':30s}  {fmt_currency(total_pnl)}")
    print(f"  {'Portfolio Return %':30s}  {fmt_pct(port_ret_pct)}")
    print(f"  {'Long Exposure (MV)':30s}  {fmt_currency(long_mv)}")
    print(f"  {'Short Exposure (MV)':30s}  {fmt_currency(short_mv)}")
    print(f"  {'Net Exposure %':30s}  {fmt_pct_plain(net_exp_pct)}")
    print(f"  {'Gross Exposure %':30s}  {fmt_pct_plain(gross_exp_pct)}")

    # --- Risk check ---
    print(f"\n  {'RISK CHECKS':}")
    flagged = False
    for r in results:
        flag = " *** FLAG: OVERSIZED ***" if r["wt_pct"] > 8.0 else ""
        print(f"  {r['ticker']:<6}  weight = {r['wt_pct']:.2f}%{flag}")
        if r["wt_pct"] > 8.0:
            flagged = True

    if flagged:
        print("\n  [!] One or more positions exceed the 8% single-position limit.")
    else:
        print("\n  [OK] All positions within the 8% single-position guideline.")

    print(f"\n{divider()}\n")


# ---------------------------------------------------------------------------
# Module 2: Capital Simulation
# ---------------------------------------------------------------------------

def _psychological_assessment(positions: list, rr_ratio: float, total_deployed_pct: float) -> str:
    lines = []

    # Concentration check
    allocs = [p["alloc_pct"] for p in positions]
    max_alloc = max(allocs) if allocs else 0
    if max_alloc > 25:
        lines.append(
            f"  HIGH CONCENTRATION: Your largest position is {max_alloc:.1f}% of capital. "
            "Concentrated conviction bets can be appropriate for high-conviction names, "
            "but ensure the thesis is stress-tested and position size reflects your edge — "
            "not your enthusiasm."
        )
    elif max_alloc > 15:
        lines.append(
            f"  MODERATE CONCENTRATION: Largest position at {max_alloc:.1f}%. "
            "This is within institutional norms for a focused book, provided the rest "
            "of the portfolio provides diversification and the stop discipline is clear."
        )
    else:
        lines.append(
            "  BALANCED SIZING: No single position dominates the book. "
            "This reflects disciplined position sizing. Ensure smaller positions still "
            "carry enough weight to move the needle on portfolio-level P&L."
        )

    # R/R commentary
    if rr_ratio >= 2.5:
        lines.append(
            f"  STRONG RISK/REWARD: Portfolio R/R of {rr_ratio:.2f}x is institutional quality. "
            "If your hit rate exceeds 40%, this book has positive expected value."
        )
    elif rr_ratio >= 1.5:
        lines.append(
            f"  ACCEPTABLE RISK/REWARD: Portfolio R/R of {rr_ratio:.2f}x is workable. "
            "Monitor hit rate closely — you need >40% wins to generate alpha at this R/R."
        )
    else:
        lines.append(
            f"  POOR RISK/REWARD: Portfolio R/R of {rr_ratio:.2f}x is below acceptable thresholds. "
            "Either your targets are too conservative, your stops are too wide, or both. "
            "Revisit the risk/reward architecture before deploying."
        )

    # Conviction mix
    convictions = [p["conviction"] for p in positions]
    avg_conv = statistics.mean(convictions) if convictions else 5
    low_conv_names = [p["ticker"] for p in positions if p["conviction"] <= 4]
    if low_conv_names:
        lines.append(
            f"  LOW-CONVICTION POSITIONS: {', '.join(low_conv_names)} have conviction <= 4. "
            "Consider whether these positions justify the capital allocation. "
            "Low-conviction positions often drag performance without compensating diversification."
        )
    else:
        lines.append(
            f"  CONVICTION AVERAGE: {avg_conv:.1f}/10. "
            "Position sizing appears aligned with conviction levels. "
            "Ensure that high-conviction names are sized proportionally larger."
        )

    # Deployment commentary
    if total_deployed_pct > 90:
        lines.append(
            "  FULLY DEPLOYED: Very little dry powder remaining. "
            "Ensure you have liquidity to meet margin calls or add to positions on weakness."
        )
    elif total_deployed_pct < 50:
        lines.append(
            f"  UNDER-DEPLOYED: Only {total_deployed_pct:.1f}% of capital is at work. "
            "High cash levels may reflect prudent caution or missed opportunity — "
            "review whether your opportunity set justifies the current deployment level."
        )

    return "\n\n".join(lines)


def module_capital_simulation(demo: bool = False):
    print(header("MODULE 2 — CAPITAL SIMULATION"))

    if demo:
        print("\n  [Demo mode] Loading demo parameters...\n")
        capital          = 500_000.0
        max_single_pct   = 20.0
        max_deployed_pct = 80.0
        raw_positions = [
            {"ticker": "VNET",  "direction": "LONG",  "conviction": 7,  "entry": 10.51, "target": 13.50, "stop": 9.00,  "alloc_pct": 10.0},
            {"ticker": "MELI",  "direction": "LONG",  "conviction": 8,  "entry": 2161.0, "target": 2600.0, "stop": 2000.0, "alloc_pct": 15.0},
            {"ticker": "SPY",   "direction": "SHORT", "conviction": 6,  "entry": 480.0, "target": 440.0, "stop": 495.0,  "alloc_pct": 12.0},
        ]
    else:
        print()
        capital          = prompt_float("  Total capital: $")
        max_single_pct   = prompt_float("  Max single position % (e.g. 20): ")
        max_deployed_pct = prompt_float("  Max total deployed % (e.g. 80): ")

        n = prompt_int("\n  Number of positions: ")
        raw_positions = []
        for i in range(n):
            print(f"\n  --- Position {i + 1} ---")
            ticker    = input("    Ticker: ").strip().upper()
            direction = prompt_choice("    Direction (Long/Short): ", ["Long", "Short"])
            conviction = prompt_int("    Conviction (1-10): ", min_val=1)
            while conviction > 10:
                print("  [!] Conviction max is 10.")
                conviction = prompt_int("    Conviction (1-10): ", min_val=1)
            entry     = prompt_float("    Entry price: $")
            target    = prompt_float("    Target price: $")
            stop      = prompt_float("    Stop price: $")
            alloc_pct = prompt_float("    Allocation % of capital: ")
            raw_positions.append({
                "ticker":     ticker,
                "direction":  direction,
                "conviction": conviction,
                "entry":      entry,
                "target":     target,
                "stop":       stop,
                "alloc_pct":  alloc_pct,
            })

    # Per-position calculations
    results = []
    for p in raw_positions:
        dollar_alloc = capital * (p["alloc_pct"] / 100.0)
        shares       = math.floor(dollar_alloc / p["entry"]) if p["entry"] != 0 else 0

        if p["direction"] == "LONG":
            exp_gain = shares * (p["target"] - p["entry"])
        else:
            exp_gain = shares * (p["entry"] - p["target"])

        max_loss  = shares * abs(p["entry"] - p["stop"])
        r_den     = abs(p["entry"] - p["stop"])
        r_mult    = abs(p["target"] - p["entry"]) / r_den if r_den != 0 else 0.0

        results.append({
            **p,
            "dollar_alloc": dollar_alloc,
            "shares":       shares,
            "exp_gain":     exp_gain,
            "max_loss":     max_loss,
            "r_mult":       r_mult,
        })

    # Portfolio summary
    total_deployed_pct  = sum(r["alloc_pct"] for r in results)
    remaining_cash      = capital * (1 - total_deployed_pct / 100.0)
    total_exp_gain      = sum(r["exp_gain"] for r in results)
    total_max_loss      = sum(r["max_loss"] for r in results)
    exp_ret_pct         = (total_exp_gain / capital * 100.0) if capital != 0 else 0.0
    rr_ratio            = (total_exp_gain / total_max_loss) if total_max_loss != 0 else 0.0

    # --- Print position table ---
    print(f"\n{divider()}")
    col = "{:<6}  {:>5}  {:>4}  {:>8}  {:>8}  {:>6}  {:>8}  {:>10}  {:>10}  {:>6}"
    print(col.format(
        "TICKER", "DIR", "CONV", "ENTRY", "TARGET", "STOP",
        "SHARES", "EXP GAIN", "MAX LOSS", "R-MULT"
    ))
    print(divider())

    for r in results:
        print(col.format(
            r["ticker"],
            r["direction"][:5],
            str(r["conviction"]),
            f"${r['entry']:,.2f}",
            f"${r['target']:,.2f}",
            f"${r['stop']:,.2f}",
            f"{r['shares']:,}",
            fmt_currency(r["exp_gain"]),
            f"-{fmt_currency(r['max_loss'])}",
            f"{r['r_mult']:.2f}x",
        ))

    print(divider())

    # --- Portfolio summary ---
    print(f"\n  {'SIMULATION SUMMARY':}")
    print(f"  {'Total Capital':35s}  {fmt_currency(capital)}")
    print(f"  {'Total Deployed':35s}  {fmt_pct_plain(total_deployed_pct)}")
    print(f"  {'Remaining Cash':35s}  {fmt_currency(remaining_cash)}")
    print(f"  {'Total Expected Gain (all targets)':35s}  {fmt_currency(total_exp_gain)}")
    print(f"  {'Total Max Loss (all stops hit)':35s}  {fmt_currency(total_max_loss)}")
    print(f"  {'Expected Return % on Capital':35s}  {fmt_pct(exp_ret_pct)}")
    print(f"  {'Risk/Reward Ratio':35s}  {rr_ratio:.2f}x")

    # --- Validation flags ---
    print(f"\n  {'VALIDATION':}")
    all_ok = True
    for r in results:
        if r["alloc_pct"] > max_single_pct:
            print(f"  [!] {r['ticker']} at {r['alloc_pct']:.1f}% exceeds max single position ({max_single_pct:.1f}%)")
            all_ok = False
    if total_deployed_pct > max_deployed_pct:
        print(f"  [!] Total deployed {total_deployed_pct:.1f}% exceeds max deployed limit ({max_deployed_pct:.1f}%)")
        all_ok = False
    if all_ok:
        print("  [OK] All positions within defined risk parameters.")

    # --- Psychological assessment ---
    print(f"\n  {'PSYCHOLOGICAL ASSESSMENT':}")
    print()
    print(_psychological_assessment(results, rr_ratio, total_deployed_pct))

    print(f"\n{divider()}\n")


# ---------------------------------------------------------------------------
# Module 3: Risk Budget
# ---------------------------------------------------------------------------

def module_risk_budget(demo: bool = False):
    print(header("MODULE 3 — RISK BUDGET"))

    if demo:
        print("\n  [Demo mode] Loading demo risk parameters...\n")
        capital          = 500_000.0
        max_port_loss    = 5.0
        max_single_loss  = 1.5
        raw_positions = [
            {"ticker": "VNET",  "entry": 10.51, "stop": 9.00,   "shares": 500,  "direction": "LONG"},
            {"ticker": "MELI",  "entry": 2161.0, "stop": 2000.0, "shares": 20,   "direction": "LONG"},
            {"ticker": "SPY",   "entry": 480.0,  "stop": 495.0,  "shares": 50,   "direction": "SHORT"},
        ]
    else:
        print()
        capital         = prompt_float("  Total capital: $")
        max_port_loss   = prompt_float("  Max portfolio drawdown % allowed (e.g. 5): ")
        max_single_loss = prompt_float("  Max single-position loss % of capital (e.g. 1.5): ")

        n = prompt_int("\n  Number of positions: ")
        raw_positions = []
        for i in range(n):
            print(f"\n  --- Position {i + 1} ---")
            ticker    = input("    Ticker: ").strip().upper()
            direction = prompt_choice("    Direction (Long/Short): ", ["Long", "Short"])
            entry     = prompt_float("    Entry price: $")
            stop      = prompt_float("    Stop price: $")
            shares    = prompt_int("    Shares: ", min_val=1)
            raw_positions.append({
                "ticker":    ticker,
                "direction": direction,
                "entry":     entry,
                "stop":      stop,
                "shares":    shares,
            })

    # Per-position risk
    results = []
    for p in raw_positions:
        risk_per_share = abs(p["entry"] - p["stop"])
        max_loss       = risk_per_share * p["shares"]
        risk_pct       = (max_loss / capital * 100.0) if capital != 0 else 0.0
        results.append({**p, "max_loss": max_loss, "risk_pct": risk_pct})

    total_risk        = sum(r["max_loss"] for r in results)
    total_risk_pct    = (total_risk / capital * 100.0) if capital != 0 else 0.0
    max_budget_dollar = capital * (max_port_loss / 100.0)
    remaining_budget  = max_budget_dollar - total_risk

    # --- Print risk table ---
    print(f"\n{divider()}")
    col = "{:<6}  {:>5}  {:>8}  {:>8}  {:>8}  {:>10}  {:>9}  {:>8}"
    print(col.format("TICKER", "DIR", "ENTRY", "STOP", "SHARES", "MAX LOSS", "RISK %", "STATUS"))
    print(divider())

    for r in results:
        if r["risk_pct"] > max_single_loss:
            status = "OVER LIMIT"
        elif r["risk_pct"] > max_single_loss * 0.75:
            status = "NEAR LIMIT"
        else:
            status = "OK"
        print(col.format(
            r["ticker"],
            r["direction"][:5],
            f"${r['entry']:,.2f}",
            f"${r['stop']:,.2f}",
            f"{r['shares']:,}",
            fmt_currency(r["max_loss"]),
            fmt_pct_plain(r["risk_pct"]),
            status,
        ))

    print(divider())

    # --- Budget summary ---
    print(f"\n  {'RISK BUDGET SUMMARY':}")
    print(f"  {'Total Capital':40s}  {fmt_currency(capital)}")
    print(f"  {'Max Portfolio Drawdown Allowed':40s}  {fmt_pct_plain(max_port_loss)}  ({fmt_currency(max_budget_dollar)})")
    print(f"  {'Total Risk Committed':40s}  {fmt_pct_plain(total_risk_pct)}  ({fmt_currency(total_risk)})")
    print(f"  {'Remaining Risk Budget':40s}  {fmt_currency(remaining_budget)}")

    if remaining_budget >= 0:
        remaining_pct = (remaining_budget / capital * 100.0)
        print(f"\n  [OK] {fmt_pct_plain(remaining_pct)} of capital ({fmt_currency(remaining_budget)}) "
              f"remains available for new risk-taking.")
    else:
        print(f"\n  [!] Risk budget EXCEEDED by {fmt_currency(abs(remaining_budget))}. "
              f"Reduce position sizes or tighten stops before adding new positions.")

    # Additional guidance
    print()
    print(f"  {'RISK BUDGET GUIDANCE':}")
    print(f"  {'':2s}• Current positions consume {total_risk_pct:.2f}% of capital in stop-loss risk.")
    print(f"  {'':2s}• Each 1% of capital represents {fmt_currency(capital * 0.01)} in absolute terms.")
    if total_risk_pct > 0:
        slots_remaining = int(remaining_budget / (total_risk / len(results))) if results else 0
        print(f"  {'':2s}• At your average risk per position ({fmt_currency(total_risk / len(results))}),")
        print(f"  {'':2s}  you have room for approximately {max(slots_remaining, 0)} more similar-sized positions.")
    print(f"  {'':2s}• Risk budget discipline prevents a string of losses from impairing your capital base.")
    print(f"  {'':2s}• Professionals rebuild capital through variance reduction, not through oversizing.")

    print(f"\n{divider()}\n")


# ---------------------------------------------------------------------------
# Main menu
# ---------------------------------------------------------------------------

MENU = """
  ╔══════════════════════════════════════════════╗
  ║     AEON PORTFOLIO CONSTRUCTION TOOL         ║
  ╠══════════════════════════════════════════════╣
  ║  1  Portfolio Builder & P&L Attribution      ║
  ║  2  Capital Simulation                       ║
  ║  3  Risk Budget                              ║
  ║  D  Run all modules in demo mode             ║
  ║  0  Exit                                     ║
  ╚══════════════════════════════════════════════╝
"""


def main():
    print(MENU)
    while True:
        choice = input("  Select module (1 / 2 / 3 / D / 0): ").strip().upper()
        if choice == "1":
            use_demo = input("  Use demo data? (y/n): ").strip().lower() == "y"
            module_portfolio_builder(demo=use_demo)
        elif choice == "2":
            use_demo = input("  Use demo data? (y/n): ").strip().lower() == "y"
            module_capital_simulation(demo=use_demo)
        elif choice == "3":
            use_demo = input("  Use demo data? (y/n): ").strip().lower() == "y"
            module_risk_budget(demo=use_demo)
        elif choice == "D":
            print("\n  Running all modules in demo mode...\n")
            module_portfolio_builder(demo=True)
            module_capital_simulation(demo=True)
            module_risk_budget(demo=True)
        elif choice == "0":
            print("\n  Goodbye.\n")
            break
        else:
            print("  [!] Invalid choice. Enter 1, 2, 3, D, or 0.")
        print(MENU)


if __name__ == "__main__":
    main()
