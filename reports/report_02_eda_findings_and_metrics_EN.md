# Report: EDA, Metrics, and Recommendations — Fit.ly Churn Analysis

## 3. Exploratory Analysis and Findings

### 3.1 Single-variable graphics

**Chart 1 – Bar chart: Customer distribution by plan type**

- Shows number of customers per plan (Free, Basic, Pro, Enterprise).
- **Finding:** Basic and Free dominate; Enterprise and Pro are smaller. Relevant because Free has the highest churn (see multi-variable chart).

**Chart 2 – Histogram: Distribution of activity count (engagement) per customer**

- Shows distribution of event count (watch_video, track_workout, read_article, share_workout) per user.
- **Finding:** Many customers have 0 events in the period; those with activity mostly have 1–4 events. This supports that low or no engagement is associated with churn.

### 3.2 Multi-variable graphic (two or more variables)

**Chart 3 – Churn by plan and by engagement**

- **Left:** Churn rate (%) by plan (Free, Basic, Pro, Enterprise).
- **Right:** Distribution of event count (engagement) for retained (churned=0) vs churned (churned=1).

**Findings:**

- **Plan:** Highest churn rate is **Free** (~41%), then Basic (~24%), Pro (~22%), Enterprise (~26%). Free customers are least “locked in” and churn most.
- **Engagement:** Mean events per user who are **retained** (~1.41) is higher than **churned** (~0.36). More active app users tend not to churn.
- **Support:** Mean tickets per user is slightly higher for churned (~2.45) vs retained (~2.23). Higher support load or poor experience may be associated with churn.

---

## 4. Metrics for the Business

### 4.1 Metrics to monitor

The business is advised to monitor **two metrics**:

1. **Churn rate (monthly or quarterly)**  
   - **Definition:** Percentage of paying (or all) customers who cancel in the period.  
   - **How to monitor:** From billing/subscription: count cancellations in period / total at start (or average).  
   - **Initial estimate (current data):**  
     - **Churn rate (snapshot):** 28.5% (114 of 400 accounts churned).  
     - Use as baseline; going forward compute per period (e.g. monthly) to track trend.

2. **Engagement rate (active customers)**  
   - **Definition:** Percentage of customers with at least one in-app activity (watch_video, track_workout, read_article, share_workout) in the period (e.g. 30 days).  
   - **How to monitor:** From activity logs: unique users with ≥1 event in window / total active (or subscribed) in same period.  
   - **Initial estimate (current data):**  
     - **Engagement rate:** 61.5% (246 of 400 with ≥1 event).  
     - Mean events per user (with activity): ~1.8.  
   - Useful because EDA shows higher engagement among non-churned customers.

### 4.2 Baseline summary

| Metric | Estimate (current data) |
|--------|--------------------------|
| Churn rate | 28.5% |
| Engagement rate | 61.5% |
| Mean events (retained) | ~1.41 per user |
| Mean events (churned) | ~0.36 per user |

---

## 5. Summary and Recommendations

### Summary

- Current churn is high (~28.5%); **Free** plan has the highest churn rate (~41%).
- **Engagement** is strongly associated with retention: more activity is associated with lower churn.
- Churned customers have slightly more support tickets on average; support experience and issue load (billing, technical, account) should be considered.

### Recommendations (actionable)

1. **Focus on Free user retention**  
   - Improve conversion Free → Basic/Pro (onboarding, limited trial, or features that encourage upgrade).  
   - Or treat Free as funnel and monitor churn separately from paid; target reducing churn for paid plans.

2. **Increase in-app engagement**  
   - Campaigns or features that encourage watch_video, track_workout, read_article, share_workout (notifications, goals, personalised content).  
   - Monitor engagement (e.g. % users with ≥1 event per 30 days) and link to churn by cohort.

3. **Monitor and improve support experience**  
   - Review ticket topics (billing, technical, account) and resolution time; reduce repeat contact and escalation.  
   - Prioritise resolving frequent billing and technical issues so they do not trigger churn.

4. **Monitor metrics regularly**  
   - Track **churn rate** by period (month/quarter) and by segment (plan, cohort).  
   - Track **engagement rate** (and mean events per user) to spot early decline and intervene before churn.

Charts referenced above are in folder `figures/` or `figures_en/`:  
`01_single_plan_distribution.png`, `02_single_event_count_histogram.png`, `03_multi_churn_by_plan_and_engagement.png`.
