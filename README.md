# Nassau Candy Distributor — Route Efficiency Dashboard

## Setup
```bash
pip install -r requirements.txt
streamlit run app.py
```
Make sure `Nassau_Candy_Distributor.csv` is in the same folder as `app.py` (it is included here).

## What's inside
- **Route Efficiency Overview** — leaderboard of Factory → State routes by shipment volume and margin, plus the raw (unreliable) lead-time field for reference.
- **Geographic View** — US choropleth of shipments/sales/margin by state, factory location map, and top congestion-candidate states.
- **Ship Mode Comparison** — shipment mix and margin by Standard/First/Second Class/Same Day.
- **Route Drill-Down** — pick any route to see its monthly order timeline, product mix, and raw order-level records.

## Filters (sidebar)
Order date range, Region, State/Province, Ship Mode, Factory, and an illustrative lead-time threshold slider.

## Known data-quality issue
The dataset's `Ship Date` field produces shipping durations of ~900–1,640 days for
every record — not physically plausible. This is documented prominently in the
dashboard's Route Efficiency tab and in the accompanying research paper. Route
rankings here use shipment volume and gross margin, which are reliable; treat any
lead-time figure in this dashboard as illustrative only until the source field is
corrected.
