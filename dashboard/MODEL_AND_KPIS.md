# Data model / KPI definitions

## Model grain
- `DimShop`: 24 shops, unique `shop_id`.
- `DimDate`: daily calendar, 2025-10-01 to 2026-09-30, unique `Date`.
- `FactFeedback`: one dated customer feedback event.
- `FactOperations`: one shop-month operational record, date stored as month start.

Relationships: `DimShop[shop_id]` to both facts; `DimDate[Date]` to both facts, where operations uses `month_start`. All are 1:* single direction. Report comparison uses **YearMonth** or year filter to avoid daily/monthly grain mismatches.

## Measures
- Total Feedback: COUNTROWS(FactFeedback).
- Total Complaints: Count filtered to feedback_type = Complaint.
- Average CSAT: arithmetic mean of 1–5 scores across feedback records.
- Negative feedback %: complaint feedback records / all feedback records (sentiment is mapped by synthetic feedback type).
- Total Transactions: sum of shop-month `transactions`.
- Complaints / 1,000 transactions: complaints / transactions * 1000; not customer prevalence, since feedback is a sample.
- Complaint Resolution %: closed complaints / all complaints.
- Average queue: transaction-weighted shop-month average.
- Stock availability: transaction-weighted shop-month average.

### Interpretational limits
This simulation generates more complaints under some higher-queue or lower-stock scenarios. Correlation here is **by design**, and is not representative of Greggs or other retailers. Real analysis would need consideration of seasonality, channel mix, repeat submissions, transaction population, shop format and complaint selection bias.
