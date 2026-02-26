"""
Fit.ly Churn Analysis - Step 3 & 4 (English)
- EDA: single-variable (2 types) + multi-variable charts + findings
- Business metrics + estimates + recommendations
"""

import pandas as pd
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use("Agg")
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

BASE = Path(__file__).resolve().parent
FIG_DIR = BASE / "figures_en"
FIG_DIR.mkdir(exist_ok=True)

# Load merged data
df = pd.read_csv(BASE / "data/da_fitly_merged.csv", sep=";")
df["churned"] = df["churned"].fillna(0).astype(int)
df["event_count"] = pd.to_numeric(df["event_count"], errors="coerce").fillna(0)
df["ticket_count"] = pd.to_numeric(df["ticket_count"], errors="coerce").fillna(0)

# ============== STEP 3: EDA & VISUALIZATION ==============

def fig_plan_bar():
    """Chart 1 - Single variable: plan distribution (bar chart)."""
    if not HAS_MPL:
        return
    plan_counts = df["plan"].value_counts().reindex(["Free", "Basic", "Pro", "Enterprise"])
    fig, ax = plt.subplots(figsize=(7, 4))
    plan_counts.plot(kind="bar", ax=ax, color=["#7f7f7f", "#1f77b4", "#ff7f0e", "#2ca02c"], edgecolor="black")
    ax.set_title("Customer Distribution by Plan Type", fontsize=12)
    ax.set_xlabel("Plan")
    ax.set_ylabel("Number of customers")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    for i, v in enumerate(plan_counts):
        ax.text(i, v + 2, str(int(v)), ha="center", fontsize=10)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "01_single_plan_distribution.png", dpi=120)
    plt.close()
    print("Saved: 01_single_plan_distribution.png (EN)")


def fig_event_histogram():
    """Chart 2 - Single variable: engagement distribution (histogram)."""
    if not HAS_MPL:
        return
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(df["event_count"], bins=range(0, int(df["event_count"].max()) + 2), color="#1f77b4", edgecolor="white")
    ax.set_title("Distribution of Activity Count per Customer (Engagement)", fontsize=12)
    ax.set_xlabel("Number of events (watch_video, track_workout, etc.)")
    ax.set_ylabel("Number of customers")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "02_single_event_count_histogram.png", dpi=120)
    plt.close()
    print("Saved: 02_single_event_count_histogram.png (EN)")


def fig_churn_by_plan_and_engagement():
    """Chart 3 - Multi variable: churn rate by plan + engagement."""
    if not HAS_MPL:
        return
    by_plan = df.groupby("plan").agg(
        total=("churned", "count"),
        churned=("churned", "sum"),
    ).assign(churn_rate=lambda x: x["churned"] / x["total"] * 100)
    by_plan = by_plan.reindex(["Free", "Basic", "Pro", "Enterprise"]).dropna(how="all")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    ax1 = axes[0]
    bars = ax1.bar(by_plan.index, by_plan["churn_rate"], color=["#7f7f7f", "#1f77b4", "#ff7f0e", "#2ca02c"], edgecolor="black")
    ax1.set_title("Churn Rate by Plan")
    ax1.set_ylabel("Churn rate (%)")
    ax1.set_xlabel("Plan")
    for b, v in zip(bars, by_plan["churn_rate"]):
        ax1.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.5, f"{v:.1f}%", ha="center", fontsize=9)

    ax2 = axes[1]
    df.boxplot(column="event_count", by="churned", ax=ax2)
    ax2.set_title("Engagement (event count) by churn status")
    ax2.set_xlabel("Churned (0 = retained, 1 = churned)")
    ax2.set_ylabel("Number of events")
    plt.suptitle("")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "03_multi_churn_by_plan_and_engagement.png", dpi=120)
    plt.close()
    print("Saved: 03_multi_churn_by_plan_and_engagement.png (EN)")


def run_eda():
    fig_plan_bar()
    fig_event_histogram()
    fig_churn_by_plan_and_engagement()


# ============== STEP 4: METRICS ==============

def compute_metrics():
    """Compute metrics and initial estimates."""
    n = len(df)
    churned = df["churned"].sum()
    churn_rate = churned / n * 100
    with_activity = (df["event_count"] > 0).sum()
    engagement_rate = with_activity / n * 100
    mean_events_active = df.loc[df["event_count"] > 0, "event_count"].mean()
    mean_events_churned = df.loc[df["churned"] == 1, "event_count"].mean()
    mean_events_retained = df.loc[df["churned"] == 0, "event_count"].mean()
    mean_tickets = df["ticket_count"].mean()
    mean_tickets_churned = df.loc[df["churned"] == 1, "ticket_count"].mean()
    mean_tickets_retained = df.loc[df["churned"] == 0, "ticket_count"].mean()
    return {
        "n": n,
        "churned": churned,
        "churn_rate_pct": churn_rate,
        "engagement_rate_pct": engagement_rate,
        "with_activity": with_activity,
        "mean_events_active": mean_events_active,
        "mean_events_churned": mean_events_churned,
        "mean_events_retained": mean_events_retained,
        "mean_tickets": mean_tickets,
        "mean_tickets_churned": mean_tickets_churned,
        "mean_tickets_retained": mean_tickets_retained,
    }


if __name__ == "__main__":
    run_eda()
    m = compute_metrics()
    print("\n--- Metric estimates (current data) ---")
    print(f"Churn rate: {m['churn_rate_pct']:.1f}% ({m['churned']}/{m['n']})")
    print(f"Engagement rate (>=1 event): {m['engagement_rate_pct']:.1f}%")
    print(f"Mean events (retained): {m['mean_events_retained']:.2f} | churned: {m['mean_events_churned']:.2f}")
    print(f"Mean tickets (retained): {m['mean_tickets_retained']:.2f} | churned: {m['mean_tickets_churned']:.2f}")
