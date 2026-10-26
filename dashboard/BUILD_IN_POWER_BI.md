# Finish and verify the native report on Windows

**Prepared source, not a tested PBIX.** This repository includes a native Power BI Project (PBIP) with three PBIR report pages, a TMSL semantic model, Power Query partitions, relationships and DAX measures. Power BI Desktop was unavailable in the authoring environment. Source-schema checks do not establish that Desktop opens or renders it correctly.

## Shortest route

1. Download the repository ZIP and extract it. Use an up-to-date Windows Power BI Desktop with Power BI Project/PBIR support enabled where required by your version.
2. Open `dashboard/CustomerFeedback/CustomerFeedback.pbip` (or the adjacent Report folder's `definition.pbir`).
3. **Transform data > Edit parameters:** change `pDataFolder` to the absolute path of your extracted `data` folder, e.g. `C:/Users/YourName/Downloads/customer-feedback-powerbi-dashboard-main/data`. No trailing slash required. Close & Apply, then Refresh. If prompted, use an appropriate local-file privacy level consistently for these synthetic sources.
4. Run `dax/validation_queries.dax` in DAX Query View, one EVALUATE query at a time. Check the baseline and region/month outputs against `validation/results.json` and `validation/expected_slices.csv`.
5. Complete the acceptance checklist below, then **File > Save As > Power BI report (.pbix)**: `dashboard/customer_feedback_insights.pbix`. Close, reopen and Refresh that PBIX.
6. Export PDF using **File > Export > Export to PDF**. Capture each page from the actual report at readable resolution and save as `screenshots/01_native_overview.png`, `02_native_operations.png`, `03_native_recommendations.png`. Commit those files only after successful verification; update README status to tested with your Desktop version and date.

The three pages and their field bindings are already authored. Import `dashboard/theme.json` under View > Themes > Browse for themes if desired; core page formatting is explicit in the PBIR source.

## Acceptance checklist (all pending Desktop execution)

- [ ] All five tables load; 24 shops, 288 operations rows, 2,438 feedback rows, 12 months and 365 calendar dates. No conversion errors.
- [ ] Five active 1:* single-direction relationships match `TECHNICAL_DOCUMENTATION.md`. No auto-created fact-to-fact or bidirectional relationship.
- [ ] Baseline: complaints 1,066; transactions 3,941,570; rate 0.270450607; average CSAT 2.849876948; negative share 43.724364%; open complaints 239.
- [ ] Choose Scotland and 2026-01 in the synced slicers; compare all cards against the matching CSV oracle row. Repeat two other region/month combinations and a noncontiguous two-month selection.
- [ ] Select a category: transaction denominator remains all transactions for the selected shops/months; only numerator changes. Clear selection afterwards.
- [ ] October 2025 previous-month and MoM measures are blank; multi-month MoM total is blank. January 2026 compares against December 2025.
- [ ] A `DimDate` daily filter blanks operational KPIs, while feedback counts still respond. Use `DimMonth[YearMonth]` on report pages.
- [ ] Right-click a shop in the overview table > Drill through > Operational Root Cause Analysis. Verify selected shop and retained region/month filters. Clear the ShopFilter in the Filters pane to reset.
- [ ] Scatter dots represent one shop for the selected period. Select one month for shop-month comparisons. Hover tooltips to verify denominator and context.
- [ ] Matrix font colour responds to rate: amber >=0.300, teal below; threshold is illustrative. If Desktop requires reapplying this: conditional formatting > Font colour > Field value > `Rate Colour`.
- [ ] Check chart axes, no clipped text, readable tooltips, keyboard navigation, synced month/region slicers and exact disclaimer on all three pages.
- [ ] Recommendations' full-period evidence is clearly static; cards respond to filters.
- [ ] PBIX opens after saving; refresh succeeds; exported PDF and actual screenshots match the report.

## Fallback if your Desktop cannot open this PBIP

Do not rename the files to `.pbix`. In a blank report create `pDataFolder` and the five blank queries from `powerquery/` (DimShop, FactOperations, FactFeedback, DimMonth, DimDate). Close & Apply. Create the five relationships in the technical documentation, mark DimDate as the date table, and paste the individual measures from `dax/measures.dax`. The PBIR JSON provides exact page coordinates, visual types and field bindings; `REPORT_SPEC.md` gives the human-readable layout. This fallback requires manual visual assembly.

Microsoft format references: [PBIP](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview), [report/PBIR](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report), [semantic model](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-dataset).
