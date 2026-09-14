import streamlit as st
from pathlib import Path
import tempfile

from toast import ToastImporter
from read import SalesReader
from analytics import Analytics


st.set_page_config(
    page_title="GrubGoblin",
    page_icon="🧌",
    layout="wide"
)

st.title("🧌 GrubGoblin")
st.caption("Restaurant sales analytics")


# Find the Toast CSV
BASE_DIR = Path(__file__).resolve().parent
TOAST_FILE = BASE_DIR / "sales.csv"

if not TOAST_FILE.exists():
    st.error("sales.csv was not found.")
    st.stop()


# Convert Toast data and run GrubGoblin analytics
try:
    with tempfile.TemporaryDirectory() as temp_dir:

        converted_file = Path(temp_dir) / "converted_sales.csv"

        importer = ToastImporter(TOAST_FILE)

        importer.import_sales(
            output_file=converted_file
        )

        reader = SalesReader(converted_file)
        sales = reader.process()

        analytics = Analytics(sales)
        summary = analytics.summary()

except Exception as e:
    st.error(f"Could not process sales data: {e}")
    st.stop()


# Dashboard
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


# Quick Insights
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


# Sales Data
st.header("Sales Data")

st.dataframe(
    sales,
    use_container_width=True,
    hide_index=True
)


# Products
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


# Revenue by Product
st.subheader("Revenue by Product")

st.bar_chart(
    product_data["revenue"]
)


# Revenue Over Time
st.subheader("Revenue Over Time")

daily_revenue = (
    sales
    .groupby("date")["revenue"]
    .sum()
)

st.line_chart(
    daily_revenue
)


# Bundle Opportunities
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


# Sales Patterns
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
