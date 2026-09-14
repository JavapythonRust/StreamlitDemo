import streamlit as st
import pandas as pd
from pathlib import Path
from itertools import combinations


# ============================================================
# PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="GrubGoblin Demo",
    page_icon="🧌",
    layout="wide"
)

st.title("🧌 GrubGoblin")
st.caption("Restaurant analytics demo")


# ============================================================
# LOAD DEMO DATA
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "sales.csv"

if not CSV_FILE.exists():
    st.error("sales.csv was not found.")
    st.stop()

try:
    raw = pd.read_csv(CSV_FILE)

except Exception as error:
    st.error(f"Could not read sales.csv: {error}")
    st.stop()


# ============================================================
# CONVERT TO GRUBGOBLIN FORMAT
# ============================================================

# This demo expects Toast-style CSV data.

column_map = {
    "Order Id": "order_id",
    "Order Date": "datetime",
    "Menu Item": "item",
    "Qty": "quantity",
    "Gross Price": "price"
}

missing = [
    column
    for column in column_map
    if column not in raw.columns
]

if missing:
    st.error(
        "The demo sales.csv is missing these Toast columns: "
        + ", ".join(missing)
    )
    st.stop()


sales = pd.DataFrame()

sales["order_id"] = raw["Order Id"]
sales["item"] = raw["Menu Item"]

sales["quantity"] = pd.to_numeric(
    raw["Qty"],
    errors="coerce"
)

sales["price"] = pd.to_numeric(
    raw["Gross Price"],
    errors="coerce"
)

sales["datetime"] = pd.to_datetime(
    raw["Order Date"],
    errors="coerce"
)

sales = sales.dropna(
    subset=[
        "order_id",
        "item",
        "quantity",
        "price",
        "datetime"
    ]
)

sales["date"] = sales["datetime"].dt.date
sales["time"] = sales["datetime"].dt.strftime("%H:%M")
sales["hour"] = sales["datetime"].dt.hour
sales["day"] = sales["datetime"].dt.day_name()

sales["revenue"] = (
    sales["quantity"] * sales["price"]
)


# ============================================================
# BASIC ANALYTICS
# ============================================================

total_revenue = sales["revenue"].sum()

total_items = sales["quantity"].sum()

total_orders = sales["order_id"].nunique()

average_order = (
    total_revenue / total_orders
    if total_orders
    else 0
)


# ============================================================
# PRODUCT ANALYTICS
# ============================================================

products = (
    sales
    .groupby("item")
    .agg(
        quantity_sold=("quantity", "sum"),
        revenue=("revenue", "sum")
    )
    .sort_values(
        "revenue",
        ascending=False
    )
)

best_seller = (
    products["quantity_sold"]
    .idxmax()
    if not products.empty
    else "N/A"
)

highest_revenue = (
    products["revenue"]
    .idxmax()
    if not products.empty
    else "N/A"
)


# ============================================================
# TIME ANALYTICS
# ============================================================

hourly = (
    sales
    .groupby("hour")["revenue"]
    .sum()
)

busiest_hour = (
    hourly.idxmax()
    if not hourly.empty
    else "N/A"
)

daily = (
    sales
    .groupby("day")["revenue"]
    .sum()
)

busiest_day = (
    daily.idxmax()
    if not daily.empty
    else "N/A"
)


# ============================================================
# BUNDLE ANALYTICS
# ============================================================

orders = (
    sales
    .groupby("order_id")["item"]
    .apply(
        lambda items: sorted(set(items))
    )
)

pair_counts = {}

for items in orders:

    for pair in combinations(items, 2):

        pair_counts[pair] = (
            pair_counts.get(pair, 0) + 1
        )


bundle_rows = []

for pair, count in pair_counts.items():

    bundle_rows.append({
        "Item 1": pair[0],
        "Item 2": pair[1],
        "Orders Together": count
    })


bundles = pd.DataFrame(bundle_rows)

if not bundles.empty:

    bundles = bundles.sort_values(
        "Orders Together",
        ascending=False
    )


# ============================================================
# DASHBOARD
# ============================================================

st.header("Dashboard")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Revenue",
        f"${total_revenue:,.2f}"
    )

with col2:
    st.metric(
        "Orders",
        f"{total_orders:,}"
    )

with col3:
    st.metric(
        "Items Sold",
        f"{total_items:,.0f}"
    )

with col4:
    st.metric(
        "Average Order",
        f"${average_order:,.2f}"
    )


# ============================================================
# INSIGHTS
# ============================================================

st.header("Key Insights")

col1, col2, col3 = st.columns(3)

with col1:

    st.subheader("Best Seller")

    st.write(best_seller)


with col2:

    st.subheader("Busiest Hour")

    st.write(
        f"{busiest_hour}:00"
    )


with col3:

    st.subheader("Busiest Day")

    st.write(busiest_day)


# ============================================================
# PRODUCT PERFORMANCE
# ============================================================

st.header("Product Performance")

st.dataframe(
    products,
    use_container_width=True
)


# ============================================================
# PRECONFIGURED CHARTS
# ============================================================

st.header("Sales Trends")

st.subheader("Revenue by Product")

st.bar_chart(
    products["revenue"]
)


st.subheader("Revenue by Day")

daily_revenue = (
    sales
    .groupby("date")["revenue"]
    .sum()
)

st.line_chart(
    daily_revenue
)


st.subheader("Revenue by Hour")

st.bar_chart(
    hourly
)


# ============================================================
# BUNDLE OPPORTUNITIES
# ============================================================

st.header("Bundle Opportunities")

if bundles.empty:

    st.info(
        "No bundle opportunities found."
    )

else:

    st.dataframe(
        bundles.head(10),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# DEMO NOTICE
# ============================================================

st.divider()

st.caption(
    "GrubGoblin demo — powered by sample restaurant sales data."
