# Native report specification

Canvas: 1440 x 900, Segoe UI, slate text, teal accents, white panels on pale grey. The exact disclaimer is placed at the bottom of every page. Month and region slicers are synced across all three pages.

| Page | Visuals and interactions |
|---|---|
| Executive overview | Four KPI cards; monthly feedback/complaint line chart; complaint-category bars; regional rate bars with numerator/denominator tooltips; shop table provides drill-through entry |
| Operational analysis | Two shop-grain scatter plots, queue and stock vs complaint rate; size = selected-period transactions; monthly rate line with MoM tooltip; region x month matrix with field-value font colour; category bars; shop detail table. This page is also a shop drill-through target |
| Management recommendations | Complaint count, open count, closure share and closed-case duration cards; three action panels; pilot design and caveats. Narrative evidence is explicitly full-period/static |

Each plot's field binding and coordinates are in its `visual.json`. Standard report page tabs provide navigation. On drill-through, clear the page's ShopFilter to return to all shops. Visual interactions, drill-through and formatting must still be tested in Desktop. If needed, reapply matrix font colour using the Rate Colour measure.

The PDF analytical briefing and its PNG pages are independently rendered summaries, not screenshots of this native report. Legacy SVGs and HTML remain separate demonstration assets.
