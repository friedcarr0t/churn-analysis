## Fit.ly Churn Analysis (English)

This repository contains an end‑to‑end churn analysis for a fictional fitness subscription app **Fit.ly**.  
The workflow covers **data validation**, **cleaning**, **dataset joining**, **exploratory data analysis (EDA)**, and **business metrics & recommendations**.

---

## 1. Project Structure

- **`da_fitly_account_info.csv`**: Customer‑level account information.
- **`da_fitly_user_activity.csv`**: In‑app behavioral events (engagement).
- **`da_fitly_customer_support.csv`**: Customer support interactions.
- **`01_validation_and_join_EN.py`**: Step 1–2 – column‑level validation, cleaning, and dataset join into a single analytical table.
- **`02_eda_and_metrics_EN.py`**: Step 3–4 – EDA charts, churn & engagement metrics, and business insights.
- **`da_fitly_merged.csv`**: Output of the join step (analytical dataset used for EDA).
- **`validation_report_EN.txt`**: Human‑readable summary of column validation checks.
- **`figures_en/`**: Folder where EDA figures are saved (created by `02_eda_and_metrics_EN.py`).

Python scripts are already written in English and are intended to be run in sequence:

1. `01_validation_and_join_EN.py`
2. `02_eda_and_metrics_EN.py`

---

## 2. Data Description

### 2.1 `da_fitly_account_info.csv` (Customer Accounts)

- **Grain**: 1 row per **customer account**.
- **Key fields**:
  - **`customer_id`**: String identifier (e.g. `C10000`), later converted to numeric `user_id`.
  - **`email`**: Customer email (unique, non‑null for almost all rows).
  - **`state`**: U.S. state (string). Used for geographic breakdowns if needed.
  - **`plan`**: Subscription plan; expected values: `Free`, `Basic`, `Pro`, `Enterprise`.
  - **`plan_list_price`**: List price of the plan. Free users have price 0.
  - **`churn_status`**: `Y` if the account has churned; blank/NaN indicates currently active.

This table defines **who the customers are**, **which plan** they are on, and **whether they have churned**.

### 2.2 `da_fitly_user_activity.csv` (Engagement Events)

- **Grain**: 1 row per **in‑app event**.
- **Key fields**:
  - **`event_time`**: Timestamp when the event occurred.
  - **`user_id`**: Numeric user ID (aligned with `customer_id` from account info).
  - **`event_type`**: Categorical activity type, such as:
    - `watch_video`
    - `track_workout`
    - `read_article`
    - `share_workout`

This table describes **how actively users interact** with Fit.ly across content types.

### 2.3 `da_fitly_customer_support.csv` (Support Tickets)

- **Grain**: 1 row per **support ticket**.
- **Key fields**:
  - **`ticket_time`**: Timestamp for ticket creation.
  - **`user_id`**: Numeric user ID.
  - **`channel`**: Contact channel (`chat`, `phone`, `email`, or `-` for unknown).
  - **`topic`**: Ticket category (e.g. `technical`, `account`, `billing`, `other`).
  - **`resolution_time_hours`**: Resolution time in hours.
  - **`state`**: Encoded ticket status (0/1), **not** geographic state.
  - **`comments`**: Free‑text comments, including GDPR‑style deletion requests.

This table summarizes **customer pain points**, **support load**, and **resolution efficiency**.

---

## 3. Data Validation & Cleaning (Step 1–2)

Implemented in **`01_validation_and_join_EN.py`**.

### 3.1 Column‑Level Validation (`validate_and_document`)

- **Account Info**:
  - Checks **row count** and **uniqueness** of `customer_id`.
  - Verifies **duplicates** on `customer_id`.
  - Summarizes **non‑null** and **unique** counts for `email`.
  - Reports the number of unique U.S. **states** and counts of nulls.
  - Compares observed `plan` values against the **expected set** `{Free, Basic, Pro, Enterprise}`.
  - Examines `plan_list_price` (min, max, null count), and confirms that **Free** plan price is 0.
  - Lists distinct `churn_status` values and null count.

- **User Activity**:
  - Parses `event_time` to datetime, computing **valid range** and **invalid datetime** count.
  - Reports **unique user count** on `user_id` and nulls.
  - Summarizes `event_type` distribution.

- **Customer Support**:
  - Parses `ticket_time` to datetime and checks for null/invalid values.
  - Counts unique `user_id` and nulls.
  - Summarizes distributions for `channel` and `topic`.
  - Computes min, max, and null count for `resolution_time_hours`.
  - Clarifies that `state` is a **0/1 ticket status** field, not geography.
  - Counts non‑empty `comments` (including deletion / GDPR‑like requests).

All validation findings are written to **`validation_report_EN.txt`**, which can be used as an appendix in a formal report.

### 3.2 Cleaning Functions

- **`clean_account(df)`**:
  - Creates numeric **`user_id`** from `customer_id` by stripping leading `"C"` and converting to `int`.
  - Derives binary **`churned`**: 1 if `churn_status == "Y"`, otherwise 0 (including missing).

- **`clean_activity(df)`**:
  - Parses `event_time` to a proper `datetime`, coercing invalid values to `NaT`.

- **`clean_support(df)`**:
  - Parses `ticket_time` to `datetime`, coercing invalid values to `NaT`.
  - Keeps `channel = "-"` as an explicit **unknown** category.

Crucially, the cleaning step **does not aggressively impute missing values**, except where required for later aggregation.

---

## 4. Dataset Join & Feature Engineering (Step 2)

Also in **`01_validation_and_join_EN.py`**.

### 4.1 Base Customer Table

- Starts from cleaned account data:
  - Keeps: `user_id`, `customer_id`, `email`, `state`, `plan`, `plan_list_price`, `churn_status`, `churned`.
  - This is the **primary customer grain** used for downstream analysis.

### 4.2 Aggregations from User Activity

From `da_fitly_user_activity.csv` the script builds:

- **`activity_agg`**:
  - **`event_count`**: total number of events per `user_id`.
  - **`event_types`**: comma‑separated list of distinct event types used by each user.
  - **`count_<event_type>`** columns (e.g. `count_watch_video`, `count_track_workout`):
    - Created via a pivot (`groupby` + `unstack`) to count each event type per user.

These features capture overall **engagement level** and **behavioral mix** of each user.

### 4.3 Aggregations from Customer Support

From `da_fitly_customer_support.csv` the script builds:

- **`support_agg`**:
  - **`ticket_count`**: number of tickets per user.
  - **`total_resolution_hours`**: total support resolution time per user.
  - **`avg_resolution_hours`**: average resolution time per ticket.
  - **`tickets_<topic>`** columns (e.g. `tickets_billing`, `tickets_technical`):
    - Created via pivot to count tickets per topic for each user.

These features quantify **support burden** and **type of issues** each user experiences.

### 4.4 Final Merge

- The script performs a **left join**:
  - `base` (one row per user)  
    ← `activity_agg` on `user_id`  
    ← `support_agg` on `user_id`
- For selected numeric columns, missing values are filled with 0 to simplify analysis:
  - Activity: `event_count`, all `count_*` columns.
  - Support: `ticket_count`, `total_resolution_hours`, `avg_resolution_hours`, all `tickets_*` columns.

The final analytical dataset is saved as:

- **`da_fitly_merged.csv`** (separator `;`)

The script prints basic join diagnostics:

- Number of accounts.
- Number of users with at least 1 activity event.
- Number of users with at least 1 support ticket.
- Total number of churned users.

---

## 5. Exploratory Data Analysis (EDA) & Visualizations (Step 3)

Implemented in **`02_eda_and_metrics_EN.py`** using `matplotlib`.  
Figures are written to **`figures_en/`**.

### 5.1 Single‑Variable Charts

- **Chart 1 – Plan distribution (`fig_plan_bar`)**
  - Shows the **count of customers per plan** (`Free`, `Basic`, `Pro`, `Enterprise`).
  - Highlights revenue‑bearing vs. free plans.

- **Chart 2 – Engagement distribution (`fig_event_histogram`)**
  - Histogram of **`event_count` per customer**.
  - Reveals the spread between **inactive**, **light**, and **heavy** users.

### 5.2 Multi‑Variable Chart

- **Chart 3 – Churn vs. plan & engagement (`fig_churn_by_plan_and_engagement`)**
  - **Left panel**: Churn rate (%) by `plan`.
  - **Right panel**: Boxplot of `event_count` split by `churned` (0 = retained, 1 = churned).

This chart helps evaluate:

- Whether **higher‑tier plans** have **lower churn**.
- How **engagement** (activity count) differs between retained vs. churned users.

---

## 6. Metrics & Business Interpretation (Step 4)

Computed in **`compute_metrics()`** within `02_eda_and_metrics_EN.py`.

### 6.1 Core Metrics

- **Churn rate**:
  - \(% churned = churned / n \times 100\)
  - Where `churned` is count of users with `churned = 1`.

- **Engagement rate**:
  - \(% engaged = (# users with event_count > 0) / n \times 100\)

- **Mean engagement**:
  - `mean_events_active`: Average `event_count` among users with at least 1 event.
  - `mean_events_churned`: Average events among churned users.
  - `mean_events_retained`: Average events among retained users.

- **Support load**:
  - `mean_tickets`: Average tickets per user overall.
  - `mean_tickets_churned`: Average tickets for churned users.
  - `mean_tickets_retained`: Average tickets for retained users.

The script prints a human‑readable summary to the console when run as `__main__`.

### 6.2 Typical Insights (Qualitative)

Although exact numbers depend on the dataset, the design of the analysis supports insights such as:

- **Churn vs. engagement**:
  - Churned users often have **lower event counts** than retained users, indicating that engagement is a strong early signal for churn.
  - Extremely low‑activity segments on paid plans may represent **at‑risk revenue**.

- **Churn vs. plan**:
  - Higher‑tier plans (e.g. `Pro`, `Enterprise`) may show **lower churn rates**, either due to higher perceived value or contractual lock‑in.
  - Free users may naturally have **higher churn** or simply churn silently without strong signals.

- **Support interaction patterns**:
  - Churned users may have **more support tickets** or more **billing / technical** topics, indicating friction points.
  - Very long `avg_resolution_hours` can correlate with dissatisfaction and possible churn.

These patterns can be confirmed and quantified using the metrics and charts produced by the scripts.

---

## 7. Recommendations for Fit.ly

Based on the structure of the analysis and typical churn patterns in subscription products, the following **actionable recommendations** are supported:

- **Strengthen early‑life engagement**
  - **Target users with low `event_count`** shortly after signup (e.g. within the first few weeks) with:
    - Onboarding tutorials, workout plans, and reminders.
    - Email/app nudges highlighting relevant content (videos, articles, programs).

- **Protect high‑value paid customers**
  - Monitor **paid plans (Basic/Pro/Enterprise)** with **declining engagement** and **recent support tickets**, especially billing or technical issues.
  - Offer **proactive outreach**, discounts, or dedicated support to retain these users.

- **Improve support experience**
  - Track **`avg_resolution_hours`** as a KPI and aim to reduce it for accounts with high churn risk.
  - Pay particular attention to topics like **billing** and **technical issues**, which often drive dissatisfaction.

- **Design churn‑prevention campaigns**
  - Combine features from `da_fitly_merged.csv` (plan, engagement, support history) into a simple **churn scoring model** or rules engine to:
    - Flag **at‑risk** users.
    - Trigger **personalized win‑back campaigns** before they churn.

- **Plan‑specific strategy**
  - If analysis shows **higher churn in Free** tier:
    - Encourage **upgrade paths** by exposing premium features with trials.
  - If a specific paid tier shows unusual churn:
    - Investigate value proposition, pricing, and feature set for that tier.