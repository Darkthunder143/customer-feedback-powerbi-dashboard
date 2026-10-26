# Technical documentation and audit

## Model and grain

| Table | Grain / key | Role |
|---|---|---|
| DimShop | One fictional shop / shop_id | Region, city, shop label and format |
| DimMonth | One calendar month / MonthStart | Shared cross-fact time dimension |
| DimDate | One day / Date | Daily feedback investigation only |
| FactFeedback | One event / feedback_id | CSAT, sentiment, category and resolution |
| FactOperations | One shop-month / shop_id + month_start | Transactions and monthly operational indicators |

Active relationships, all 1:* and single direction from dimension to fact:

| Dimension key | Fact foreign key |
|---|---|
| DimShop[shop_id] | FactFeedback[shop_id] |
| DimShop[shop_id] | FactOperations[shop_id] |
| DimMonth[MonthStart] | FactFeedback[month_start] |
| DimMonth[MonthStart] | FactOperations[month_start] |
| DimDate[Date] | FactFeedback[feedback_date] |

No date-to-month relationship and no fact-to-fact joins. This prevents ambiguous filter paths. Daily filters have no valid daily operational denominator: `Total Transactions` explicitly returns BLANK when DimDate is cross-filtered. Dependent operational KPIs consequently return BLANK. All report slicers and monthly axes use DimMonth. Do not expose feedback_date directly as a cross-fact slicer: use the date dimension for daily investigation, with the guard measure.

## Power Query

Queries load original UTF-8 CSV files with quoted-field support. pDataFolder is a local folder parameter; both slash styles and trailing separators are accepted. Types use en-GB locale. CSAT and transactions are integers; dates are Date; rates are fractions, not 0-100 values. Empty resolution hours are converted to null before numeric conversion. Feedback receives a derived month_start. DimMonth covers every month between min/max operational dates; DimDate spans the complete calendar interval. Query dependencies are acyclic. No raw CSV is edited, no rows are silently removed, and no imputation converts open-case duration to zero.

## Measures and interpretation

- Count events, not unique customers: there is no customer identifier.
- Negative share counts sentiment = Negative divided by all feedback in context; type and sentiment are equivalent in this generator, but the measure uses the sentiment field directly.
- Complaint/closure measures use KEEPFILTERS, so a Compliment-only filter does not unexpectedly restore complaints.
- Complaint rates are SUM(complaints) / SUM(transactions) * 1,000, never averages of shop rates.
- Category selection filters feedback only; transaction exposure remains the complete selected shop/month population. Do not interpret category, order-channel or product-specific rates as incidence within that channel/product: no corresponding transaction breakdown exists.
- Queue and stock metrics are transaction-weighted averages of shop-month indicators. Stock weighting is a portfolio convention, not a claim that the source is a transaction-level availability survey.
- Prior-month comparison requires exactly one month and a prior operational observation; otherwise returns blank. MoM uses prior-month complaints, not the monthly rate.
- Closed-case duration excludes open cases. It is not an SLA compliance metric or mean time to resolution for all complaints. No created/closed timestamps, as-of snapshot or backlog-age fields exist.
- Rate Colour uses a 0.300 illustrative display threshold, not an employer target.

## Analysis and limitations

Original data: 24 shops, 12 months, 288 operational observations, 2,438 feedback events. Independent segmentation is performed by exact shop_id + month_start; never by region-month. Queue >=6 minutes: 529 complaints / 1,642,607 transactions = 0.322049 per 1K; below 6: 537 / 2,298,963 = 0.233584. Availability <93%: 581 / 1,883,034 = 0.308545; at least 93%: 485 / 2,058,536 = 0.235604.

Unweighted Pearson correlation across the 288 shop-month rates: queue r=0.3102; stock r=-0.2751. These are descriptive, not statistical proof. Repeated observations within shops are not independent; no causal or significance claim is made. Report scatter plots instead show one transaction-weighted point per shop for the currently selected period. Select one month to see shop-month grain. Do not equate the full-period shop plot with the 288-row correlation calculation.

The generator creates 6-11 feedback events per shop-month independently of transaction volume, and explicitly increases complaint probability with queue time and lower stock. Rates can therefore vary due to synthetic sampling and denominator effects; this is a demonstration, not an empirical operational study. There are no real comments to analyse, no meaningful sentiment model, and no validated commercial benefit. Real work would need governed data, response propensity, seasonality, qualitative review, shop format, severity, repeat contacts, channel exposure and controlled pilots.

## Audit fixes

1. Replaced shared daily-calendar filtering of monthly operations with a conformed month dimension and daily-filter guard.
2. Added explicit null handling for open-case hours and integer types.
3. Made filter intersection explicit with KEEPFILTERS and defined single-month time intelligence.
4. Fixed original HTML segmentation: region-month keys merged three shops; added shop IDs to both embedded datasets and matched shop-month keys.
5. Fixed rate labels rounded to integers in the browser preview.
6. Added a distinct complaint-follow-up recommendation supported by 239 open cases; no overdue/SLA claim.
7. Added native editable project source, executable analysis checks and honest status labels. Existing illustrative SVGs remain legacy designs and are not native screenshots.

## Verification boundary

`python scripts/validate_project.py`: 425 data/arithmetic checks, complete region/month oracle and shop-month comparisons. Source CSV hashes recorded in results.json. `node scripts/check_preview.js`: exercises actual preview render logic and segmentation baseline across all 117 region/month views. `validate_native_source.py`: Microsoft JSON schemas, relationship/field references and canvas bounds. Neither Python nor schema validation executes M or DAX. No Power BI rendering, refresh, interaction, PBIX save/reopen or exported screenshot is claimed.

Run all scripts from the repository root. Analysis uses Python standard library; native schema validation needs jsonschema and access to developer.microsoft.com. PDF generation needs pandas, matplotlib and reportlab. The final acceptance checklist is in BUILD_IN_POWER_BI.md.
