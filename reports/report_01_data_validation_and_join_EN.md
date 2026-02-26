# Report: Data Validation & Join — Fit.ly Churn Analysis

## 1. Data Validation and Cleaning (Step 1)

Data from three sources (account, activity, support) were validated column by column. Per the Lead Engineer: data are not validated in the pipeline, updated daily, and missing/irregular values can occur. Below are the validation and cleaning steps applied.

### 1.1 Account info (`da_fitly_account_info.csv`)

| Column | Validation | Findings | Cleaning step |
|--------|------------|----------|---------------|
| **customer_id** | Unique, format C + 5 digits | 400 rows, 400 unique, no duplicates | Unchanged. Used to create join key `user_id` (numeric part only). |
| **email** | Non-null, unique | 400 non-null, 400 unique | Unchanged. |
| **state** | Valid values (US state) | 50 states, 0 null | Unchanged. Per PM: location from billing. |
| **plan** | Matches product definition | Values: Free, Basic, Pro, Enterprise | Unchanged. Matches tiers from PM. |
| **plan_list_price** | Numeric, ≥ 0 | Min 0, max 148; 105 rows with 0 (Free) | Unchanged. Free = 0 as expected. |
| **churn_status** | "Y" = churned, blank = active | 114 "Y", 286 blank (active) | For analysis: created binary `churned` (1 = Y, 0 = no). Blank values left as-is. |

### 1.2 User activity (`da_fitly_user_activity.csv`)

| Column | Validation | Findings | Cleaning step |
|--------|------------|----------|---------------|
| **event_time** | Datetime format | Range Jun–Dec 2025, 0 invalid | Parsed to `datetime` for time analysis. |
| **user_id** | Integer, consistent with account | 246 unique users with activity | Unchanged. Used as join key. |
| **event_type** | Fixed categories | read_article, watch_video, track_workout, share_workout | Unchanged. |

**Note:** Not all accounts have rows in activity (400 accounts vs 246 users with activity). Users with no activity remain in the account table; on join they receive aggregate 0.

### 1.3 Customer support (`da_fitly_customer_support.csv`)

| Column | Validation | Findings | Cleaning step |
|--------|------------|----------|---------------|
| **ticket_time** | Datetime (Pacific, per PM) | All valid | Parsed to `datetime`. |
| **user_id** | Consistent with account | 367 unique users with tickets | Unchanged. |
| **channel** | Category | chat, phone, email, and "-" (39 tickets) | "-" left as unknown; not imputed. |
| **topic** | Category | technical, account, other, billing | Unchanged. |
| **resolution_time_hours** | Numeric, ≥ 0 | Min ~0.52, max ~32.46, 0 null | Unchanged. Per PM: ticket open to close. |
| **state** | Not US state | Values 0 and 1 (ticket status) | Unchanged. Distinct from account state. |
| **comments** | Optional text | 46 non-empty; some GDPR-style deletion requests | Unchanged. Per PM: deletion requests are normal and not highlighted as missing. |

No row deletion or imputation that changes data interpretation; only type standardization (datetime, churn binary) for analysis.

---

## 2. Join Strategy (Step 2)

### 2.1 Join key

- **Account** uses `customer_id` (format C10000, C10001, …).
- **User activity** and **customer support** use `user_id` (numeric: 10000, 10001, …).
- **Mapping:** `user_id = integer from customer_id` (strip prefix "C"). Example: C10000 → 10000. One account row maps to one user_id in activity and support.

### 2.2 Join approach

- **Base:** One row per account from `account_info` (400 rows).
- **Activity:** Aggregated by `user_id`: event count, counts per `event_type` (count_read_article, count_watch_video, count_track_workout, count_share_workout).
- **Support:** Aggregated by `user_id`: ticket count, total and mean resolution_time_hours, ticket counts per topic (tickets_account, tickets_billing, tickets_other, tickets_technical).
- **Join:** Left join account to activity_agg, then to support_agg. All 400 accounts retained; users with no activity/tickets get aggregate 0 (not dropped).

### 2.3 Output

- **File:** `da_fitly_merged.csv`
- **Dimensions:** 400 rows × 21 columns
- **Summary:**
  - 400 accounts (base)
  - 246 users with ≥ 1 activity
  - 367 users with ≥ 1 support ticket
  - 114 users churned (churn_status = Y)

This merged dataset is ready for churn EDA (engagement, support, plan) and metric calculation.
