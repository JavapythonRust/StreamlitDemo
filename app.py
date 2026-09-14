import streamlit as st
from pathlib import Path

from read import SalesReader
from analytics import Analytics


# -----------------------------
# Page setup
# -----------------------------

st.set_page_config(
    page_title="GrubGoblin",
    page_icon="🧌",
    layout="wide"
)

st.title("🧌 GrubGoblin")
st.caption("Restaurant sales analytics")


# -----------------------------
# Load dummy sales data
# -----------------------------

BASE_DIR = Path(__file__).resolve().parent
SALES_FILE = BASE_DIR / "sales.csv"

if not SALES_FILE.exists():
    st.error("sales.csv was not found.")
    st.stop()


# -----------------------------
# Process sales using
# existing GrubGoblin code
# -----------------------------

try:
    reader = SalesReader(SALES_FILE)
    sales = reader.process()

    analytics = Analytics(sales)
    summary = analytics.summary()

except Exception as e:
    st.error(f"Could not process sales data: {e}")
    st.stop()


# -----------------------------
# Dashboard metrics
# -----------------------------

st.header("Dashboard")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Revenue",
        f"${summary['total_revenue']:,.2f}"
    )

with col2:
    st.metric(
        "Orders",
        f"{summary['total_orders']:,}"
    )

with col3:
    st.metric(
        "Items Sold",
        f"{summary['total_items_sold']:,}"
    )

with col4:
    st.metric(
        "Average Order",
        f"${summary['average_order_value']:,.2f}"
    )


# -----------------------------
# Quick insights
# -----------------------------

st.header("Quick Insights")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Best Seller")
    st.write(summary["best_selling_product"])

with col2:
    st.subheader("Busiest Hour")
    st.write(summary["busiest_hour"])

with col3:
    st.subheader("Busiest Day")
    st.write(summary["busiest_day"])


# -----------------------------
# Sales data
# -----------------------------

st.header("Sales Data")

st.dataframe(
    sales,
    use_container_width=True,
    hide_index=True
)


# -----------------------------
# Product performance
# -----------------------------

st.header("Products")

product_data = (
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

st.dataframe(
    product_data,
    use_container_width=True
)


# -----------------------------
# Revenue by product
# -----------------------------

st.subheader("Revenue by Product")

st.bar_chart(
    product_data["revenue"]
)


# -----------------------------
# Revenue over time
# -----------------------------

st.subheader("Revenue Over Time")

daily_revenue = (
    sales
    .groupby("date")["revenue"]
    .sum()
)

st.line_chart(
    daily_revenue
)


# -----------------------------
# Bundle opportunities
# -----------------------------

st.header("Bundle Opportunities")

bundles = summary.get(
    "bundle_opportunities",
    []
)

if bundles is not None and len(bundles) > 0:
    st.dataframe(
        bundles,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No bundle opportunities found.")


# -----------------------------
# Patterns
# -----------------------------

st.header("Sales Patterns")

patterns = summary.get(
    "patterns",
    []
)

if patterns:
    for pattern in patterns:
        st.write(
            f"**{pattern['type']}** — "
            f"{pattern['description']}"
        )
else:
    st.info("No patterns found.")
