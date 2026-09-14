import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
from itertools import combinations


class Grapher:
    def __init__(
        self,
        sales,
        graph_dir="graphs"
    ):
        self.sales = sales.copy()

        self.graph_dir = Path(
            graph_dir
        )

        self.graph_dir.mkdir(
            exist_ok=True
        )

    # -------------------------
    # BUSIEST HOURS
    # -------------------------

    def busiest_hours(self):
        hourly = (
            self.sales
            .groupby("hour")["quantity"]
            .sum()
        )

        plt.figure(figsize=(10, 5))

        hourly.plot(
            kind="bar"
        )

        plt.title("Busiest Hours")
        plt.xlabel("Hour")
        plt.ylabel("Items Sold")
        plt.tight_layout()

        path = (
            self.graph_dir
            / "busiest_hours.png"
        )

        plt.savefig(path)
        plt.close()

        return path

    # -------------------------
    # BUSIEST DAYS
    # -------------------------

    def busiest_days(self):
        day_order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
        ]

        daily = (
            self.sales
            .groupby("day")["quantity"]
            .sum()
            .reindex(day_order)
            .fillna(0)
        )

        plt.figure(figsize=(10, 5))

        daily.plot(
            kind="bar"
        )

        plt.title("Busiest Days")
        plt.xlabel("Day")
        plt.ylabel("Items Sold")
        plt.tight_layout()

        path = (
            self.graph_dir
            / "busiest_days.png"
        )

        plt.savefig(path)
        plt.close()

        return path

    # -------------------------
    # TOP PRODUCTS
    # -------------------------

    def top_products(self):
        products = (
            self.sales
            .groupby("item")["revenue"]
            .sum()
            .sort_values(
                ascending=False
            )
            .head(10)
        )

        plt.figure(figsize=(10, 6))

        products.sort_values().plot(
            kind="barh"
        )

        plt.title(
            "Top 10 Products by Revenue"
        )

        plt.xlabel("Revenue ($)")
        plt.ylabel("Product")
        plt.tight_layout()

        path = (
            self.graph_dir
            / "top_products.png"
        )

        plt.savefig(path)
        plt.close()

        return path

    # -------------------------
    # LOW-PERFORMING PRODUCTS
    # -------------------------

    def low_performing_products(self):
        products = (
            self.sales
            .groupby("item")["revenue"]
            .sum()
            .sort_values()
            .head(10)
        )

        plt.figure(figsize=(10, 6))

        products.plot(
            kind="barh"
        )

        plt.title(
            "Lowest Performing Products"
        )

        plt.xlabel("Revenue ($)")
        plt.ylabel("Product")
        plt.tight_layout()

        path = (
            self.graph_dir
            / "low_performing_products.png"
        )

        plt.savefig(path)
        plt.close()

        return path

    # -------------------------
    # REVENUE OVER TIME
    # -------------------------

    def revenue_over_time(self):
        daily = (
            self.sales
            .groupby(
                self.sales["datetime"].dt.date
            )["revenue"]
            .sum()
        )

        plt.figure(figsize=(10, 5))

        daily.plot(
            kind="line",
            marker="o"
        )

        plt.title(
            "Revenue Over Time"
        )

        plt.xlabel("Date")
        plt.ylabel("Revenue ($)")
        plt.tight_layout()

        path = (
            self.graph_dir
            / "revenue_over_time.png"
        )

        plt.savefig(path)
        plt.close()

        return path

    # -------------------------
    # MONTHLY REVENUE
    # -------------------------

    def monthly_revenue(self):
        monthly = (
            self.sales
            .groupby("month")["revenue"]
            .sum()
        )

        monthly.index = (
            monthly.index.astype(str)
        )

        plt.figure(figsize=(10, 5))

        monthly.plot(
            kind="line",
            marker="o"
        )

        plt.title(
            "Monthly Revenue"
        )

        plt.xlabel("Month")
        plt.ylabel("Revenue ($)")
        plt.tight_layout()

        path = (
            self.graph_dir
            / "monthly_revenue.png"
        )

        plt.savefig(path)
        plt.close()

        return path

    # -------------------------
    # MONTHLY ITEMS
    # -------------------------

    def monthly_items_sold(self):
        monthly = (
            self.sales
            .groupby("month")["quantity"]
            .sum()
        )

        monthly.index = (
            monthly.index.astype(str)
        )

        plt.figure(figsize=(10, 5))

        monthly.plot(
            kind="bar"
        )

        plt.title(
            "Items Sold by Month"
        )

        plt.xlabel("Month")
        plt.ylabel("Items Sold")
        plt.tight_layout()

        path = (
            self.graph_dir
            / "monthly_items_sold.png"
        )

        plt.savefig(path)
        plt.close()

        return path

    # -------------------------
    # MONTHLY AVERAGE ORDER
    # -------------------------

    def monthly_average_order_value(self):
        order_totals = (
            self.sales
            .groupby(
                ["month", "order_id"]
            )["revenue"]
            .sum()
        )

        monthly_aov = (
            order_totals
            .groupby(level=0)
            .mean()
        )

        monthly_aov.index = (
            monthly_aov.index.astype(str)
        )

        plt.figure(figsize=(10, 5))

        monthly_aov.plot(
            kind="line",
            marker="o"
        )

        plt.title(
            "Monthly Average Order Value"
        )

        plt.xlabel("Month")
        plt.ylabel(
            "Average Order Value ($)"
        )

        plt.tight_layout()

        path = (
            self.graph_dir
            / "monthly_average_order_value.png"
        )

        plt.savefig(path)
        plt.close()

        return path

    # -------------------------
    # POPULAR BUNDLES
    # -------------------------

    def popular_bundles(self):
        order_items = (
            self.sales
            .groupby("order_id")["item"]
            .apply(
                lambda items: sorted(set(items))
            )
        )

        bundle_counts = {}

        for items in order_items:
            for pair in combinations(
                items,
                2
            ):
                bundle_counts[pair] = (
                    bundle_counts.get(pair, 0)
                    + 1
                )

        bundles = pd.Series(
            bundle_counts
        ).sort_values(
            ascending=False
        ).head(10)

        if bundles.empty:
            return None

        labels = [
            f"{pair[0]} + {pair[1]}"
            for pair in bundles.index
        ]

        plt.figure(figsize=(10, 6))

        plt.barh(
            labels[::-1],
            bundles.values[::-1]
        )

        plt.title(
            "Most Popular Product Bundles"
        )

        plt.xlabel(
            "Orders Containing Both Products"
        )

        plt.ylabel(
            "Product Combination"
        )

        plt.tight_layout()

        path = (
            self.graph_dir
            / "popular_bundles.png"
        )

        plt.savefig(path)
        plt.close()

        return path

    # -------------------------
    # DAY-PART GRAPH
    # -------------------------

    def day_parts(self):
        if "day_part" not in self.sales.columns:

            def get_day_part(hour):
                if 5 <= hour < 7:
                    return "Early Morning"

                if 7 <= hour < 10:
                    return "Breakfast"

                if 10 <= hour < 12:
                    return "Late Morning"

                if 12 <= hour < 14:
                    return "Lunch"

                if 14 <= hour < 17:
                    return "Afternoon"

                if hour >= 17:
                    return "Evening"

                return "Before 5 AM"

            self.sales["day_part"] = (
                self.sales["hour"]
                .apply(get_day_part)
            )

        order = [
            "Early Morning",
            "Breakfast",
            "Late Morning",
            "Lunch",
            "Afternoon",
            "Evening",
            "Before 5 AM"
        ]

        revenue = (
            self.sales
            .groupby("day_part")["revenue"]
            .sum()
            .reindex(order)
            .dropna()
        )

        plt.figure(figsize=(10, 5))

        revenue.plot(
            kind="bar"
        )

        plt.title(
            "Revenue by Day Part"
        )

        plt.xlabel("Day Part")
        plt.ylabel("Revenue ($)")
        plt.tight_layout()

        path = (
            self.graph_dir
            / "day_parts.png"
        )

        plt.savefig(path)
        plt.close()

        return path

    # -------------------------
    # GENERATE ALL
    # -------------------------

    def generate_all(self):
        generated = []

        graph_functions = [
            self.busiest_hours,
            self.busiest_days,
            self.top_products,
            self.low_performing_products,
            self.revenue_over_time,
            self.monthly_revenue,
            self.monthly_items_sold,
            self.monthly_average_order_value,
            self.popular_bundles,
            self.day_parts
        ]

        for function in graph_functions:
            path = function()

            if path is not None:
                generated.append(path)

        return generated


if __name__ == "__main__":
    sales = pd.read_csv("sales.csv")

    sales["revenue"] = (
        sales["quantity"]
        * sales["price"]
    )

    sales["datetime"] = pd.to_datetime(
        sales["date"].astype(str)
        + " "
        + sales["time"].astype(str)
    )

    sales["hour"] = sales["datetime"].dt.hour
    sales["day"] = sales["datetime"].dt.day_name()
    sales["month"] = sales["datetime"].dt.to_period("M")

    grapher = Grapher(sales)

    grapher.generate_all()

    print(
        "Graphs generated successfully."
    )
