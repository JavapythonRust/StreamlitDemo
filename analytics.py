import pandas as pd
from itertools import combinations


class Analytics:
    def __init__(self, sales):
        self.sales = sales.copy()

    # -------------------------
    # BASIC SALES
    # -------------------------

    def total_revenue(self):
        return self.sales["revenue"].sum()

    def total_items_sold(self):
        return self.sales["quantity"].sum()

    def total_orders(self):
        return self.sales["order_id"].nunique()

    def average_order_value(self):
        order_totals = (
            self.sales
            .groupby("order_id")["revenue"]
            .sum()
        )

        if order_totals.empty:
            return 0

        return order_totals.mean()

    # -------------------------
    # PRODUCTS
    # -------------------------

    def product_sales(self):
        return (
            self.sales
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

    def best_selling_product(self):
        products = (
            self.sales
            .groupby("item")["quantity"]
            .sum()
            .sort_values(ascending=False)
        )

        if products.empty:
            return "—"

        return products.index[0]

    def highest_revenue_product(self):
        products = (
            self.sales
            .groupby("item")["revenue"]
            .sum()
            .sort_values(ascending=False)
        )

        if products.empty:
            return "—"

        return products.index[0]

    def lowest_revenue_product(self):
        products = (
            self.sales
            .groupby("item")["revenue"]
            .sum()
            .sort_values()
        )

        if products.empty:
            return "—"

        return products.index[0]

    # -------------------------
    # TIME ANALYSIS
    # -------------------------

    def busiest_hour(self):
        hourly = (
            self.sales
            .groupby("hour")["quantity"]
            .sum()
        )

        if hourly.empty:
            return "—"

        return hourly.idxmax()

    def busiest_day(self):
        daily = (
            self.sales
            .groupby("day")["quantity"]
            .sum()
        )

        if daily.empty:
            return "—"

        return daily.idxmax()

    def least_busy_day(self):
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

        if daily.empty:
            return "—"

        return daily.idxmin()

    def average_daily_revenue(self):
        daily = (
            self.sales
            .groupby(
                self.sales["datetime"].dt.date
            )["revenue"]
            .sum()
        )

        if daily.empty:
            return 0

        return daily.mean()

    # -------------------------
    # MONTHLY ANALYSIS
    # -------------------------

    def monthly_revenue(self):
        return (
            self.sales
            .groupby("month")["revenue"]
            .sum()
        )

    def monthly_items_sold(self):
        return (
            self.sales
            .groupby("month")["quantity"]
            .sum()
        )

    def monthly_average_order_value(self):
        monthly_orders = (
            self.sales
            .groupby(
                ["month", "order_id"]
            )["revenue"]
            .sum()
        )

        return (
            monthly_orders
            .groupby(level=0)
            .mean()
        )

    def monthly_revenue_change(self):
        monthly = self.monthly_revenue()

        return monthly.pct_change() * 100

    # -------------------------
    # BUNDLE ANALYSIS
    # -------------------------

    def popular_bundles(self, limit=10):
        order_items = (
            self.sales
            .groupby("order_id")["item"]
            .apply(
                lambda items: sorted(set(items))
            )
        )

        bundle_counts = {}

        for items in order_items:
            for pair in combinations(items, 2):
                bundle_counts[pair] = (
                    bundle_counts.get(pair, 0) + 1
                )

        if not bundle_counts:
            return pd.DataFrame(
                columns=[
                    "product_1",
                    "product_2",
                    "orders_together"
                ]
            )

        bundles = (
            pd.Series(bundle_counts)
            .sort_values(ascending=False)
            .head(limit)
        )

        results = []

        for pair, count in bundles.items():
            results.append({
                "product_1": pair[0],
                "product_2": pair[1],
                "orders_together": count
            })

        return pd.DataFrame(results)

    def bundle_opportunities(self, limit=10):
        bundles = self.popular_bundles(limit)

        if bundles.empty:
            return bundles

        bundles["opportunity"] = (
            bundles["orders_together"]
            .apply(self._bundle_strength)
        )

        return bundles

    @staticmethod
    def _bundle_strength(order_count):
        if order_count >= 100:
            return "Strong"

        if order_count >= 50:
            return "Moderate"

        return "Possible"

    # -------------------------
    # DAY-PART ANALYSIS
    # -------------------------

    def add_day_parts(self):
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

    def day_part_analysis(self):
        if "day_part" not in self.sales.columns:
            self.add_day_parts()

        analysis = (
            self.sales
            .groupby("day_part")
            .agg(
                revenue=("revenue", "sum"),
                items_sold=("quantity", "sum"),
                orders=("order_id", "nunique")
            )
        )

        analysis["average_order_value"] = (
            analysis["revenue"]
            / analysis["orders"]
        )

        day_part_order = [
            "Early Morning",
            "Breakfast",
            "Late Morning",
            "Lunch",
            "Afternoon",
            "Evening",
            "Before 5 AM"
        ]

        analysis = analysis.reindex(
            [
                part
                for part in day_part_order
                if part in analysis.index
            ]
        )

        analysis["most_popular_product"] = [
            self.day_part_popular_products(part) or "—"
            for part in analysis.index
        ]

        return analysis
        # -------------------------
    # PATTERN ANALYSIS
    # -------------------------

    # Below this many distinct calendar days of data, correlation-based
    # patterns are considered unreliable and are labeled accordingly
    # rather than presented as confident findings.
    MIN_RELIABLE_DAYS = 14

    def distinct_days(self):
        if self.sales.empty:
            return 0

        return self.sales["datetime"].dt.date.nunique()

    def has_reliable_history(self):
        return self.distinct_days() >= self.MIN_RELIABLE_DAYS

    def product_relationships(
        self,
        min_correlation=0.50,
        limit=20
    ):
        """
        Finds products whose sales tend to move together.

        Uses daily quantity sold for each product and
        calculates Pearson correlation.

        Correlation:
            +1.0 = strongly move together
             0.0 = little/no linear relationship
            -1.0 = move in opposite directions
        """

        daily_products = (
            self.sales
            .groupby(
                [
                    self.sales["datetime"].dt.date,
                    "item"
                ]
            )["quantity"]
            .sum()
            .unstack(fill_value=0)
        )

        if daily_products.shape[1] < 2:
            return pd.DataFrame(
                columns=[
                    "item_1",
                    "item_2",
                    "correlation",
                    "relationship"
                ]
            )

        correlations = daily_products.corr()

        results = []

        items = correlations.columns.tolist()

        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                item_1 = items[i]
                item_2 = items[j]

                correlation = correlations.loc[
                    item_1,
                    item_2
                ]

                if pd.isna(correlation):
                    continue

                if abs(correlation) < min_correlation:
                    continue

                if correlation >= 0.75:
                    relationship = "Strong positive"
                elif correlation >= 0.50:
                    relationship = "Positive"
                elif correlation <= -0.75:
                    relationship = "Strong negative"
                else:
                    relationship = "Negative"

                results.append({
                    "item_1": item_1,
                    "item_2": item_2,
                    "correlation": correlation,
                    "relationship": relationship
                })

        if not results:
            return pd.DataFrame(
                columns=[
                    "item_1",
                    "item_2",
                    "correlation",
                    "relationship"
                ]
            )

        return (
            pd.DataFrame(results)
            .sort_values(
                "correlation",
                key=abs,
                ascending=False
            )
            .head(limit)
            .reset_index(drop=True)
        )

    def product_co_occurrence(
        self,
        min_orders=2,
        limit=20
    ):
        """
        Finds products that frequently appear
        in the same orders.
        """

        order_items = (
            self.sales
            .groupby("order_id")["item"]
            .apply(
                lambda items: sorted(set(items))
            )
        )

        if order_items.empty:
            return pd.DataFrame(
                columns=[
                    "item_1",
                    "item_2",
                    "orders_together"
                ]
            )

        pair_counts = {}

        for items in order_items:
            for pair in combinations(items, 2):
                pair_counts[pair] = (
                    pair_counts.get(pair, 0) + 1
                )

        results = []

        for pair, count in pair_counts.items():
            if count < min_orders:
                continue

            results.append({
                "item_1": pair[0],
                "item_2": pair[1],
                "orders_together": count
            })

        if not results:
            return pd.DataFrame(
                columns=[
                    "item_1",
                    "item_2",
                    "orders_together"
                ]
            )

        return (
            pd.DataFrame(results)
            .sort_values(
                "orders_together",
                ascending=False
            )
            .head(limit)
            .reset_index(drop=True)
        )

    def patterns(self, limit=20):
        """
        General-purpose pattern summary.

        Combines:
            - Sales correlations
            - Product co-occurrence
        """

        relationships = self.product_relationships(
            limit=limit
        )

        co_occurrence = self.product_co_occurrence(
            limit=limit
        )

        patterns = []

        reliable = self.has_reliable_history()

        for _, row in relationships.iterrows():
            correlation = row["correlation"]

            if correlation >= 0:
                description = (
                    f"{row['item_1']} and "
                    f"{row['item_2']} tend to sell "
                    f"more or less together."
                )
            else:
                description = (
                    f"{row['item_1']} and "
                    f"{row['item_2']} tend to move "
                    f"in opposite directions."
                )

            if not reliable:
                description += (
                    f" (Based on only {self.distinct_days()} day(s) of "
                    "data — treat as a tentative pattern, not a "
                    "confirmed trend.)"
                )

            patterns.append({
                "type": "Sales relationship",
                "item_1": row["item_1"],
                "item_2": row["item_2"],
                "strength": abs(correlation),
                "description": description
            })

        for _, row in co_occurrence.iterrows():
            patterns.append({
                "type": "Order relationship",
                "item_1": row["item_1"],
                "item_2": row["item_2"],
                "strength": row["orders_together"],
                "description": (
                    f"{row['item_1']} and "
                    f"{row['item_2']} appeared together "
                    f"in {int(row['orders_together'])} orders."
                )
            })

        return patterns[:limit]
    def day_part_popular_products(self, day_part):
        if "day_part" not in self.sales.columns:
            self.add_day_parts()

        filtered = self.sales[
            self.sales["day_part"] == day_part
        ]

        if filtered.empty:
            return None

        products = (
            filtered
            .groupby("item")["quantity"]
            .sum()
            .sort_values(ascending=False)
        )

        if products.empty:
            return None

        return products.index[0]

    # -------------------------
    # PRODUCT PERFORMANCE MATRIX
    # -------------------------

    def product_performance_matrix(self):
        """
        Classifies each product into one of four quadrants based on
        whether its quantity sold and revenue are above or below the
        median product's quantity/revenue. Median (not mean) is used
        so a single outlier item can't skew every other product's
        classification.

        Quadrants:
            High volume / High revenue — reliable core sellers
            High volume / Low revenue  — popular but thin margin;
                                          candidates for a price look
            Low volume / High revenue  — pricey items worth promoting
            Low volume / Low revenue   — candidates for menu review

        Needs at least 2 distinct products to be meaningful; returns
        an empty frame otherwise.
        """

        products = self.product_sales()

        columns = [
            "quantity_sold",
            "revenue",
            "quadrant"
        ]

        if len(products) < 2:
            return pd.DataFrame(columns=columns)

        quantity_median = products["quantity_sold"].median()
        revenue_median = products["revenue"].median()

        def classify(row):
            high_volume = row["quantity_sold"] >= quantity_median
            high_revenue = row["revenue"] >= revenue_median

            if high_volume and high_revenue:
                return "High volume / High revenue"

            if high_volume and not high_revenue:
                return "High volume / Low revenue"

            if not high_volume and high_revenue:
                return "Low volume / High revenue"

            return "Low volume / Low revenue"

        result = products.copy()
        result["quadrant"] = result.apply(classify, axis=1)

        return result[columns]

    # -------------------------
    # SUMMARY
    # -------------------------

    def summary(self):
        return {
            "total_revenue": self.total_revenue(),
            "total_items_sold": self.total_items_sold(),
            "total_orders": self.total_orders(),
            "patterns": self.patterns(),
            "average_order_value": (
                self.average_order_value()
            ),
            "best_selling_product": (
                self.best_selling_product()
            ),
            "highest_revenue_product": (
                self.highest_revenue_product()
            ),
            "lowest_revenue_product": (
                self.lowest_revenue_product()
            ),
            "busiest_hour": self.busiest_hour(),
            "busiest_day": self.busiest_day(),
            "least_busy_day": self.least_busy_day(),
            "average_daily_revenue": (
                self.average_daily_revenue()
            ),
            "bundle_opportunities": (
                self.bundle_opportunities()
            ),
            "day_part_analysis": (
                self.day_part_analysis()
            ),
            "product_performance_matrix": (
                self.product_performance_matrix()
            )
        }


if __name__ == "__main__":
    sales = pd.read_csv("sales.csv")

    sales["revenue"] = (
        sales["quantity"] * sales["price"]
    )

    sales["datetime"] = pd.to_datetime(
        sales["date"].astype(str)
        + " "
        + sales["time"].astype(str)
    )

    sales["hour"] = sales["datetime"].dt.hour
    sales["day"] = sales["datetime"].dt.day_name()
    sales["month"] = sales["datetime"].dt.to_period("M")

    analytics = Analytics(sales)

    print(
        "Total Revenue:",
        analytics.total_revenue()
    )

    print(
        "Total Orders:",
        analytics.total_orders()
    )

    print(
        "Average Order Value:",
        analytics.average_order_value()
    )

    print(
        "\nDay-Part Analysis:"
    )

    print(
        analytics.day_part_analysis()
    )
