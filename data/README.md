# Synthetic datasets

All records are fictional. Source period: **1 October 2025 to 30 September 2026**, using complete calendar months. Dates use ISO 8601.

| File | Grain | Rows | Purpose |
|---|---|---:|---|
| `shops.csv` | One row per sample shop | 24 | Shop geography and format |
| `operations.csv` | One row per shop per month | 288 | Fictional transactions, queues, stock and staffing |
| `feedback.csv` | One row per feedback event | 2438 | Fictional comments, CSAT, status and category |

## Relationships
`shops.shop_id` (1) → `feedback.shop_id` (many) and `operations.shop_id` (many). A dedicated calendar relates at day grain to `feedback.feedback_date` and on month-start dates to `operations.month_start`. **Compare feedback and operational KPIs at month or year grain**, not at individual day grain, since operational observations are monthly.

## Data dictionary
**Feedback:** `feedback_id`, `feedback_date`, `shop_id`, `feedback_channel` (contact route), `feedback_type` (Complaint / Compliment / Suggestion), `category` (subject), `sentiment` (rule-based fictional classification), `csat_score` (integer 1–5), `severity`, `resolution_status`, `resolution_hours` (empty if open), `product_category`, `order_channel`, `feedback_text` (fictional template).

**Operations:** `shop_id`, `month_start`, `transactions`, `avg_queue_minutes`, `stock_availability_pct` (fraction from 0–1), `avg_basket_gbp`, `staffing_hours`, `on_time_online_orders_pct` (fraction 0–1).

**Shops:** `shop_id`, `shop_label`, `city`, `region`, `format`.

Notes: Complaint incidence is deliberately influenced by shop-month queue time and stock availability to make an educational investigation possible; these *programmed* associations are not market research or evidence about any real organisation. Feedback is a nonrepresentative synthetic sample, so raw regional complaint counts should not be confused with customer dissatisfaction prevalence. Use complaints per 1,000 fictional transactions for exposure-adjusted comparisons.
