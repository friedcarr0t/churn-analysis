"""
Fit.ly Churn Analysis - Step 1 & 2 (English)
- Validation and cleaning per column (documentation)
- Join account_info + user_activity + customer_support
"""

import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent

# ============== LOAD RAW DATA ==============
account = pd.read_csv(BASE / "data/da_fitly_account_info.csv", sep=",")
activity = pd.read_csv(BASE / "data/da_fitly_user_activity.csv", sep=",")
support = pd.read_csv(BASE / "data/da_fitly_customer_support.csv", sep=",")

# ============== STEP 1: VALIDATION PER COLUMN ==============

def validate_and_document():
    """Validate each column and record findings (for report)."""
    findings = []

    # --- account_info ---
    findings.append("=== ACCOUNT INFO ===")
    cust_ids = account["customer_id"]
    findings.append(f"  customer_id: {len(cust_ids)} rows, {cust_ids.nunique()} unique. Format Cxxxxx.")
    findings.append(f"    Duplicates: {(cust_ids.duplicated()).sum()}")
    findings.append(f"  email: {account['email'].notna().sum()} non-null, {account['email'].nunique()} unique.")
    findings.append(f"  state: {account['state'].nunique()} unique (US states). Null: {account['state'].isna().sum()}")
    expected_plans = {"Free", "Basic", "Pro", "Enterprise"}
    plans = set(account["plan"].dropna().unique())
    findings.append(f"  plan: values {sorted(plans)}. Matches PM: {plans <= expected_plans}")
    findings.append(f"  plan_list_price: min={account['plan_list_price'].min()}, max={account['plan_list_price'].max()}. Null: {account['plan_list_price'].isna().sum()}")
    findings.append(f"    Free plan price 0: {(account['plan_list_price'] == 0).sum()} rows.")
    churn_vals = account["churn_status"].dropna().unique()
    findings.append(f"  churn_status: values {list(churn_vals)} (Y = churned). Blank = active. Null count: {account['churn_status'].isna().sum()}")

    # --- user_activity ---
    findings.append("\n=== USER ACTIVITY ===")
    findings.append(f"  event_time: dtype {activity['event_time'].dtype}. Null: {activity['event_time'].isna().sum()}")
    act_dt = pd.to_datetime(activity["event_time"], errors="coerce")
    findings.append(f"    Range: {act_dt.min()} to {act_dt.max()}. Invalid: {act_dt.isna().sum()}")
    findings.append(f"  user_id: {activity['user_id'].nunique()} unique users. Null: {activity['user_id'].isna().sum()}")
    findings.append(f"  event_type: {activity['event_type'].value_counts().to_dict()}")

    # --- customer_support ---
    findings.append("\n=== CUSTOMER SUPPORT ===")
    sup_dt = pd.to_datetime(support["ticket_time"], errors="coerce")
    findings.append(f"  ticket_time: Null: {support['ticket_time'].isna().sum()}. Invalid datetime: {sup_dt.isna().sum()}")
    findings.append(f"  user_id: {support['user_id'].nunique()} unique. Null: {support['user_id'].isna().sum()}")
    findings.append(f"  channel: {support['channel'].value_counts().to_dict()}")
    findings.append(f"  topic: {support['topic'].value_counts().to_dict()}")
    findings.append(f"  resolution_time_hours: min={support['resolution_time_hours'].min():.2f}, max={support['resolution_time_hours'].max():.2f}. Null: {support['resolution_time_hours'].isna().sum()}")
    findings.append(f"  state: values {sorted(support['state'].dropna().unique().astype(int).tolist())} (0/1 - ticket status, not US state). Null: {support['state'].isna().sum()}")
    non_empty_comments = (support["comments"].notna() & (support["comments"].astype(str).str.strip() != "")).sum()
    findings.append(f"  comments: non-empty {non_empty_comments} (incl. GDPR-style requests).")

    return "\n".join(findings)


def clean_account(df):
    """Standardise for analysis. Do not alter missing."""
    df = df.copy()
    df["user_id"] = df["customer_id"].str.replace("C", "", regex=False).astype(int)
    df["churned"] = (df["churn_status"].fillna("") == "Y").astype(int)
    return df


def clean_activity(df):
    """Parse datetime. Do not alter missing."""
    df = df.copy()
    df["event_time"] = pd.to_datetime(df["event_time"], errors="coerce")
    return df


def clean_support(df):
    """Standardise. Channel '-' left as unknown."""
    df = df.copy()
    df["ticket_time"] = pd.to_datetime(df["ticket_time"], errors="coerce")
    return df


# Run validation and save summary
validation_report = validate_and_document()
report_path = BASE / "validation_report_EN.txt"
with open(report_path, "w", encoding="utf-8") as f:
    f.write("DATA VALIDATION - Fit.ly Churn\n")
    f.write("=" * 50 + "\n\n")
    f.write(validation_report)
print("Validation report (EN) saved to:", report_path)

# Apply cleaning
account_clean = clean_account(account)
activity_clean = clean_activity(activity)
support_clean = clean_support(support)

# ============== STEP 2: JOIN ==============
base = account_clean[["user_id", "customer_id", "email", "state", "plan", "plan_list_price", "churn_status", "churned"]].copy()

activity_agg = activity_clean.groupby("user_id").agg(
    event_count=("event_type", "count"),
    event_types=("event_type", lambda x: ", ".join(sorted(x.unique()))),
).reset_index()
event_counts = activity_clean.groupby(["user_id", "event_type"]).size().unstack(fill_value=0)
event_counts.columns = [f"count_{c}" for c in event_counts.columns]
activity_agg = activity_agg.merge(event_counts.reset_index(), on="user_id", how="left")

support_agg = support_clean.groupby("user_id").agg(
    ticket_count=("ticket_time", "count"),
    total_resolution_hours=("resolution_time_hours", "sum"),
    avg_resolution_hours=("resolution_time_hours", "mean"),
).reset_index()
topic_counts = support_clean.groupby(["user_id", "topic"]).size().unstack(fill_value=0)
topic_counts.columns = [f"tickets_{c}" for c in topic_counts.columns]
support_agg = support_agg.merge(topic_counts.reset_index(), on="user_id", how="left")

merged = base.merge(activity_agg, on="user_id", how="left")
merged = merged.merge(support_agg, on="user_id", how="left")

act_cols = [c for c in merged.columns if c.startswith("count_") or c == "event_count"]
sup_cols = ["ticket_count", "total_resolution_hours", "avg_resolution_hours"] + [c for c in merged.columns if c.startswith("tickets_")]
for c in act_cols + sup_cols:
    if c in merged.columns:
        merged[c] = merged[c].fillna(0)

merged_path = BASE / "da_fitly_merged.csv"
merged.to_csv(merged_path, index=False, sep=";")
print("Merged dataset saved to:", merged_path)
print("Shape:", merged.shape)

print("\n--- Join summary ---")
print("Accounts (base):", len(base))
print("With at least 1 activity:", (merged["event_count"].fillna(0) > 0).sum())
print("With at least 1 support ticket:", (merged["ticket_count"].fillna(0) > 0).sum())
print("Churned (Y):", merged["churned"].sum())
