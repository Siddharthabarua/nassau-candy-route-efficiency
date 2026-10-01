"""
Nassau Candy Distributor — Factory-to-Customer Shipping Route Efficiency Dashboard
Run with:  streamlit run app.py
Requires:  Nassau_Candy_Distributor.csv in the same folder (or update DATA_PATH below).
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

DATA_PATH = "Nassau_Candy_Distributor.csv"

st.set_page_config(page_title="Nassau Candy | Route Efficiency", layout="wide", page_icon="🍬")

PRODUCT_FACTORY = {
    'Wonka Bar - Nutty Crunch Surprise': "Lot's O' Nuts",
    'Wonka Bar - Fudge Mallows': "Lot's O' Nuts",
    'Wonka Bar -Scrumdiddlyumptious': "Lot's O' Nuts",
    'Wonka Bar - Milk Chocolate': "Wicked Choccy's",
    'Wonka Bar - Triple Dazzle Caramel': "Wicked Choccy's",
    'Laffy Taffy': 'Sugar Shack',
    'SweeTARTS': 'Sugar Shack',
    'Nerds': 'Sugar Shack',
    'Fun Dip': 'Sugar Shack',
    'Fizzy Lifting Drinks': 'Sugar Shack',
    'Everlasting Gobstopper': 'Secret Factory',
    'Hair Toffee': 'The Other Factory',
    'Lickable Wallpaper': 'Secret Factory',
    'Wonka Gum': 'Secret Factory',
    'Kazookles': 'The Other Factory',
}
FACTORY_COORDS = {
    "Lot's O' Nuts": (32.881893, -111.768036),
    "Wicked Choccy's": (32.076176, -81.088371),
    "Sugar Shack": (48.11914, -96.18115),
    "Secret Factory": (41.446333, -90.565487),
    "The Other Factory": (35.1175, -89.971107),
}

STATE_ABBR = {
    'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA','Colorado':'CO',
    'Connecticut':'CT','Delaware':'DE','Florida':'FL','Georgia':'GA','Hawaii':'HI','Idaho':'ID',
    'Illinois':'IL','Indiana':'IN','Iowa':'IA','Kansas':'KS','Kentucky':'KY','Louisiana':'LA',
    'Maine':'ME','Maryland':'MD','Massachusetts':'MA','Michigan':'MI','Minnesota':'MN',
    'Mississippi':'MS','Missouri':'MO','Montana':'MT','Nebraska':'NE','Nevada':'NV',
    'New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM','New York':'NY',
    'North Carolina':'NC','North Dakota':'ND','Ohio':'OH','Oklahoma':'OK','Oregon':'OR',
    'Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC','South Dakota':'SD',
    'Tennessee':'TN','Texas':'TX','Utah':'UT','Vermont':'VT','Virginia':'VA','Washington':'WA',
    'West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY','District of Columbia':'DC',
}


@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df["OrderDate"] = pd.to_datetime(df["Order Date"], format="%d-%m-%Y")
    df["ShipDate"] = pd.to_datetime(df["Ship Date"], format="%d-%m-%Y")
    df["LeadTimeDays_RAW"] = (df["ShipDate"] - df["OrderDate"]).dt.days
    df["Factory"] = df["Product Name"].map(PRODUCT_FACTORY)
    df["Route"] = df["Factory"] + " \u2192 " + df["State/Province"]
    df["Margin_Pct"] = df["Gross Profit"] / df["Sales"] * 100
    df["StateAbbr"] = df["State/Province"].map(STATE_ABBR)
    return df


try:
    df = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(f"Could not find '{DATA_PATH}'. Place the CSV file in the same folder as app.py.")
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.title("🍬 Nassau Candy")
st.sidebar.caption("Route Efficiency Dashboard")
st.sidebar.markdown("---")

min_date, max_date = df["OrderDate"].min().date(), df["OrderDate"].max().date()
date_range = st.sidebar.date_input("Order date range", value=(min_date, max_date),
                                    min_value=min_date, max_value=max_date)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

regions = sorted(df["Region"].unique())
sel_regions = st.sidebar.multiselect("Region", regions, default=regions)

states = sorted(df["State/Province"].unique())
sel_states = st.sidebar.multiselect("State / Province", states, default=[])

ship_modes = sorted(df["Ship Mode"].unique())
sel_modes = st.sidebar.multiselect("Ship Mode", ship_modes, default=ship_modes)

factories = sorted(df["Factory"].unique())
sel_factories = st.sidebar.multiselect("Factory", factories, default=factories)

st.sidebar.markdown("---")
leadtime_threshold = st.sidebar.slider(
    "Lead-time threshold (days) — for illustration only, see data-quality notice",
    min_value=0, max_value=1700, value=30, step=10,
)
st.sidebar.caption(
    "⚠️ The Ship Date field in this dataset is not reliable (see notice on the "
    "Route Efficiency tab). This slider is provided per the dashboard spec but "
    "will flag ~100% of shipments as 'delayed' until the source data is corrected."
)

mask = (
    (df["OrderDate"].dt.date >= start_date)
    & (df["OrderDate"].dt.date <= end_date)
    & (df["Region"].isin(sel_regions))
    & (df["Ship Mode"].isin(sel_modes))
    & (df["Factory"].isin(sel_factories))
)
if sel_states:
    mask &= df["State/Province"].isin(sel_states)

fdf = df[mask].copy()

if fdf.empty:
    st.warning("No shipments match the current filters. Adjust the filters in the sidebar.")
    st.stop()

# ---------------------------------------------------------------------------
# Header + KPI row
# ---------------------------------------------------------------------------
st.title("Factory-to-Customer Shipping Route Efficiency")
st.caption("Nassau Candy Distributor — interactive analytics dashboard")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Shipments", f"{len(fdf):,}")
k2.metric("Sales", f"${fdf['Sales'].sum():,.0f}")
k3.metric("Gross Profit", f"${fdf['Gross Profit'].sum():,.0f}")
k4.metric("Avg. Margin", f"{fdf['Gross Profit'].sum() / fdf['Sales'].sum() * 100:.1f}%")
pct_over = (fdf["LeadTimeDays_RAW"] > leadtime_threshold).mean() * 100
k5.metric(f"% Over {leadtime_threshold}d (raw field)", f"{pct_over:.1f}%",
          help="Based on the unreliable Ship Date field — see data-quality notice.")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Route Efficiency Overview", "🗺️ Geographic View", "🚚 Ship Mode Comparison", "🔎 Route Drill-Down"]
)

# ---------------------------------------------------------------------------
# TAB 1 — Route Efficiency Overview
# ---------------------------------------------------------------------------
with tab1:
    st.warning(
        "**Data quality notice:** the Ship Date field in this dataset produces shipping "
        "durations of ~900–1,640 days for 100% of records, which is not physically "
        "plausible. Lead-time-based KPIs below are shown for completeness but should "
        "not be treated as accurate until the source field is corrected. Route rankings "
        "in this tab are based on **shipment volume and gross margin**, which are reliable.",
        icon="⚠️",
    )

    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("Route Performance Leaderboard (Factory → State)")
        route_perf = (
            fdf.groupby("Route")
            .agg(Shipments=("Order ID", "count"), Sales=("Sales", "sum"),
                 Profit=("Gross Profit", "sum"), AvgLeadTime_raw=("LeadTimeDays_RAW", "mean"))
            .reset_index()
        )
        route_perf["Margin_%"] = route_perf["Profit"] / route_perf["Sales"] * 100
        route_perf = route_perf.sort_values("Shipments", ascending=False)
        top_n = st.slider("Show top N routes by volume", 5, 30, 15, key="topn_routes")
        show = route_perf.head(top_n).sort_values("Shipments")
        fig = px.bar(show, x="Shipments", y="Route", orientation="h",
                     color="Margin_%", color_continuous_scale="Purples",
                     labels={"Margin_%": "Margin %"})
        fig.update_layout(height=max(350, 24 * top_n), margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Avg. Lead Time by Route (raw field)")
        st.caption("⚠️ Unreliable — see notice above")
        lt = route_perf.sort_values("AvgLeadTime_raw").head(10)
        fig2 = px.bar(lt, x="AvgLeadTime_raw", y="Route", orientation="h",
                      color_discrete_sequence=["#C0392B"])
        fig2.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10),
                            xaxis_title="Days (raw, unreliable)")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Route table")
    st.dataframe(
        route_perf.style.format({"Sales": "${:,.2f}", "Profit": "${:,.2f}",
                                  "Margin_%": "{:.1f}%", "AvgLeadTime_raw": "{:.0f}"}),
        use_container_width=True, height=300,
    )

# ---------------------------------------------------------------------------
# TAB 2 — Geographic View
# ---------------------------------------------------------------------------
with tab2:
    st.subheader("US Shipment & Efficiency Heatmap")

    geo = (
        fdf.groupby(["State/Province", "StateAbbr"])
        .agg(Shipments=("Order ID", "count"), Sales=("Sales", "sum"),
             Profit=("Gross Profit", "sum"), AvgLeadTime_raw=("LeadTimeDays_RAW", "mean"))
        .reset_index()
    )
    geo["Margin_%"] = geo["Profit"] / geo["Sales"] * 100
    geo_us = geo.dropna(subset=["StateAbbr"])

    metric_choice = st.radio("Color states by:", ["Shipments", "Sales", "Margin_%"], horizontal=True)
    fig_map = px.choropleth(
        geo_us, locations="StateAbbr", locationmode="USA-states", color=metric_choice,
        scope="usa", color_continuous_scale="Purples",
        hover_data={"State/Province": True, "Shipments": True, "Sales": ":.2f", "Margin_%": ":.1f"},
    )
    fig_map.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=500)
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("#### Factory locations")
    fac_df = pd.DataFrame(
        [{"Factory": f, "lat": c[0], "lon": c[1],
          "Shipments": (fdf["Factory"] == f).sum()} for f, c in FACTORY_COORDS.items()]
    )
    fig_fac = px.scatter_geo(
        fac_df, lat="lat", lon="lon", text="Factory", size="Shipments",
        scope="usa", color_discrete_sequence=["#E8A33D"],
    )
    fig_fac.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=420)
    st.plotly_chart(fig_fac, use_container_width=True)

    st.markdown("#### Congestion candidates — top states by shipment volume")
    st.dataframe(
        geo_us.sort_values("Shipments", ascending=False).head(15)
        .style.format({"Sales": "${:,.2f}", "Profit": "${:,.2f}", "Margin_%": "{:.1f}%"}),
        use_container_width=True,
    )

# ---------------------------------------------------------------------------
# TAB 3 — Ship Mode Comparison
# ---------------------------------------------------------------------------
with tab3:
    st.subheader("Ship Mode Performance")
    sm = (
        fdf.groupby("Ship Mode")
        .agg(Shipments=("Order ID", "count"), Sales=("Sales", "sum"),
             Profit=("Gross Profit", "sum"), AvgLeadTime_raw=("LeadTimeDays_RAW", "mean"))
        .reset_index()
    )
    sm["Margin_%"] = sm["Profit"] / sm["Sales"] * 100
    sm["Share_%"] = sm["Shipments"] / sm["Shipments"].sum() * 100

    c1, c2 = st.columns(2)
    with c1:
        fig3 = px.pie(sm, names="Ship Mode", values="Shipments", hole=0.35,
                       color_discrete_sequence=px.colors.sequential.Purples_r)
        fig3.update_layout(title="Shipment Mix by Ship Mode", height=380)
        st.plotly_chart(fig3, use_container_width=True)
    with c2:
        fig4 = px.bar(sm, x="Ship Mode", y="Margin_%", color="Ship Mode",
                       color_discrete_sequence=px.colors.sequential.Purples_r)
        fig4.update_layout(title="Gross Margin % by Ship Mode", height=380, showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

    st.info(
        "Margins are essentially flat across ship modes — shipping method in this dataset "
        "is a cost/service lever, not a profitability driver. Genuine speed comparisons "
        "(e.g. Same Day vs. Standard Class) cannot be confirmed until Ship Date is corrected.",
        icon="ℹ️",
    )
    st.dataframe(
        sm.style.format({"Sales": "${:,.2f}", "Profit": "${:,.2f}", "Margin_%": "{:.1f}%",
                          "Share_%": "{:.1f}%", "AvgLeadTime_raw": "{:.0f}"}),
        use_container_width=True,
    )

# ---------------------------------------------------------------------------
# TAB 4 — Route Drill-Down
# ---------------------------------------------------------------------------
with tab4:
    st.subheader("Route Drill-Down")
    route_options = sorted(fdf["Route"].unique())
    chosen_route = st.selectbox("Select a Factory → State route", route_options)

    rdf = fdf[fdf["Route"] == chosen_route]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Shipments", f"{len(rdf):,}")
    c2.metric("Sales", f"${rdf['Sales'].sum():,.0f}")
    c3.metric("Margin", f"{rdf['Gross Profit'].sum() / rdf['Sales'].sum() * 100:.1f}%")
    c4.metric("Avg Units/Order", f"{rdf['Units'].mean():.1f}")

    st.markdown("#### Order-level shipment timeline (Order Date)")
    ts = rdf.groupby(rdf["OrderDate"].dt.to_period("M")).agg(
        Shipments=("Order ID", "count"), Sales=("Sales", "sum")
    ).reset_index()
    ts["OrderDate"] = ts["OrderDate"].dt.to_timestamp()
    fig5 = px.line(ts, x="OrderDate", y="Shipments", markers=True,
                    color_discrete_sequence=["#5B2C83"])
    fig5.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("#### Product mix on this route")
    pm = rdf.groupby("Product Name").agg(
        Units=("Units", "sum"), Sales=("Sales", "sum")
    ).reset_index().sort_values("Sales", ascending=False)
    st.dataframe(pm.style.format({"Sales": "${:,.2f}"}), use_container_width=True)

    st.markdown("#### Raw order-level records for this route")
    st.dataframe(
        rdf[["Order ID", "OrderDate", "ShipDate", "Ship Mode", "City", "Product Name",
             "Sales", "Units", "Gross Profit"]].sort_values("OrderDate"),
        use_container_width=True, height=300,
    )

st.markdown("---")
st.caption(
    "Built for Nassau Candy Distributor · Route definitions: Factory → Customer Region / "
    "State, per product-factory mapping. See the accompanying research paper for the full "
    "methodology and the Ship Date data-quality finding."
)
