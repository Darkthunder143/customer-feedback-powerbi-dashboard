# Assemble the native interactive Power BI report

This repository already contains the dataset, build instructions, DAX, Power Query scripts and an independently interactive HTML demo. **It does not contain an actual PBIX file.** A validated `.pbix` must be saved by Power BI Desktop; no tool here can author/test its native format.

## A. Import and clean data (15–20 minutes)
1. Download the repository ZIP, extract it, and locate the `data` folder.
2. Open **Power BI Desktop → Transform data → Power Query editor**.
3. Make a **Text parameter** called `pDataFolder`, e.g. `C:\\Users\\YourName\\Downloads\\customer-feedback-powerbi-dashboard\\data\\` (include trailing slash/backslash).
4. Create blank queries named **FactFeedback**, **FactOperations**, **DimShop**. In **Advanced Editor**, paste the corresponding files from `powerquery/`.
5. Verify numeric, date and percentage columns, then **Close & Apply**.
6. In Modeling → New table, paste the `DimDate` definition from `dax/measures.dax`; mark it as a date table on [Date].

## B. Relationships
- DimShop[shop_id] (1) → FactFeedback[shop_id] (*) **single direction**.
- DimShop[shop_id] (1) → FactOperations[shop_id] (*) **single direction**.
- DimDate[Date] (1) → FactFeedback[feedback_date] (*) **single direction**.
- DimDate[Date] (1) → FactOperations[month_start] (*) **single direction**.
- Ensure `Month Name` sorts by `Month Number` (or prefer `YearMonth` slicers).
- **Important:** FactOperations is a monthly table. Compare operations and feedback by *calendar month or year*. Selecting a random individual date will remove monthly operational rows and invalidate transaction-denominator comparisons. For production, build a month-level comparison layer if day-level filtering is required.

## C. Create DAX measures
Create each measure, one at a time, using `Modeling → New measure`, and paste individual definitions from `dax/measures.dax`. Set % formats on rate measures. Do not paste the entire text into one measure.

## D. Build 3 report pages

### Page 1 — Executive Overview
- Four KPI cards: Total Feedback, Average CSAT, Negative Feedback %, Complaints per 1K Transactions.
- Line chart: DimDate[YearMonth] vs Total Feedback.
- Horizontal bar: FactFeedback[category] vs Total Complaints.
- Region bar: DimShop[region] vs Complaints per 1K Transactions.
- Slicers: DimDate[YearMonth], DimShop[region], FactFeedback[feedback_type]. **Caution:** feedback-type slicer affects the complaint/negative-share measures and can skew the executive overview. Use page-specific filter interactions or remove that slicer from KPI cards.

### Page 2 — Root Causes
- Scatter: FactOperations[avg_queue_minutes] on X vs Complaints per 1K Transactions on Y, with Shop and YearMonth as detail grain; monthly store grain is critical.
- Bar: complaint rate by region and category.
- Heatmap/matrix: Month × Region with complaint rates.
- Drill-through: DimShop[shop_label] showing feedback detail table with no real identifiers.

### Page 3 — Management Actions
- KPI cards: Total Complaints, Complaint Resolution %, Average Resolved Complaint Hours, Total Transactions.
- Bar chart with top categories by complaint count.
- Three short text panels based on `insights/executive_summary.md`.
- Highlight explicitly that all findings refer to simulated data.

## E. Report formatting
Use one background colour, high-contrast readable text, meaningful chart headings, aligned visuals and page navigation. Add a visible footer on every page: **PORTFOLIO DEMONSTRATION · SYNTHETIC DATA · NOT GREGGS CUSTOMER INFORMATION**. Enable useful tooltips, bookmarks or drill-through and test interaction behaviour.

## F. Validate and save
Expected checks for the checked-in sample data:
- Shops: 24; shop-month rows: 288; feedback rows: 2438.
- Total Complaints: 1066; Total Transactions: 3941570.
- Overall Average CSAT: 2.850; complaint rate per 1k: 0.2705.
- For any month, ensure the transaction denominator sums *all 24 shop rows* for that month.
- Test slicers and non-additivity of rates; check blank filter handling.
- Save as `dashboard/customer_feedback_insights.pbix`. Take real Power BI screenshots and replace the illustrative SVG previews in `screenshots/`.

## G. Sharing safely
Before sharing publicly, confirm no real customer data, confidential sales data, internal shop identifiers, unpublished documents or proprietary content is present. Do not imply endorsement by Greggs or any other employer.
