# Model and KPI index

The revised authoritative specification is [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md).

DimShop and **DimMonth** filter both facts. DimDate filters feedback only. Do not use the old daily-date-to-monthly-operations relationship. Cross-fact report filters must use DimMonth[YearMonth]. Daily DimDate selections intentionally blank transaction-based rates.

Native project: [CustomerFeedback/CustomerFeedback.pbip](CustomerFeedback/CustomerFeedback.pbip). All original CSVs are preserved. Source validation is complete; Power BI Desktop acceptance testing is pending.
