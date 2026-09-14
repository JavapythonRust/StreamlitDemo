import pandas as pd


REQUIRED_COLUMNS = {
    "date",
    "time",
    "order_id",
    "item",
    "quantity",
    "price"
}


class SalesReader:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.sales = None
        self.products = None
        # Human-readable notes about rows that were skipped or data
        # that looked suspicious. Surfaced to the user, never silent.
        self.warnings = []

    def read(self):
        self.sales = pd.read_csv(self.csv_file)

        if self.sales.empty:
            raise ValueError(
                "The CSV file has no rows. Please check the export."
            )

        missing_columns = REQUIRED_COLUMNS - set(self.sales.columns)

        if missing_columns:
            raise ValueError(
                "Missing required columns: "
                + ", ".join(sorted(missing_columns))
            )

        return self.sales

    def prepare(self):
        if self.sales is None:
            self.read()

        self.warnings = []
        starting_rows = len(self.sales)

        # --- quantity / price: coerce instead of hard-crashing ---
        self.sales["quantity"] = pd.to_numeric(
            self.sales["quantity"],
            errors="coerce"
        )

        self.sales["price"] = pd.to_numeric(
            self.sales["price"],
            errors="coerce"
        )

        bad_numbers = (
            self.sales["quantity"].isna()
            | self.sales["price"].isna()
        )

        if bad_numbers.any():
            self.warnings.append(
                f"Skipped {int(bad_numbers.sum())} row(s) with a "
                "non-numeric quantity or price."
            )

        self.sales = self.sales[~bad_numbers]

        # --- negative or zero quantity/price: suspicious, not fatal ---
        negative_quantity = self.sales["quantity"] < 0
        negative_price = self.sales["price"] < 0

        if negative_quantity.any():
            self.warnings.append(
                f"Found {int(negative_quantity.sum())} row(s) with a "
                "negative quantity (possible refund/void). They were "
                "kept but may affect totals — review your export if "
                "this is unexpected."
            )

        if negative_price.any():
            self.warnings.append(
                f"Skipped {int(negative_price.sum())} row(s) with a "
                "negative price."
            )

        self.sales = self.sales[~negative_price]

        # --- blank product names ---
        blank_item = (
            self.sales["item"].isna()
            | (self.sales["item"].astype(str).str.strip() == "")
        )

        if blank_item.any():
            self.warnings.append(
                f"Skipped {int(blank_item.sum())} row(s) with a "
                "missing product name."
            )

        self.sales = self.sales[~blank_item]

        # --- missing order id ---
        blank_order = (
            self.sales["order_id"].isna()
            | (self.sales["order_id"].astype(str).str.strip() == "")
        )

        if blank_order.any():
            self.warnings.append(
                f"Skipped {int(blank_order.sum())} row(s) with a "
                "missing order ID."
            )

        self.sales = self.sales[~blank_order]

        if self.sales.empty:
            raise ValueError(
                "No usable rows remained after data validation. "
                "Please check the CSV file."
            )

        self.sales["revenue"] = (
            self.sales["quantity"]
            * self.sales["price"]
        )

        self.sales["datetime"] = pd.to_datetime(
            self.sales["date"].astype(str)
            + " "
            + self.sales["time"].astype(str),
            errors="coerce"
        )

        bad_dates = self.sales["datetime"].isna()

        if bad_dates.any():
            self.warnings.append(
                f"Skipped {int(bad_dates.sum())} row(s) with an "
                "unreadable date or time."
            )

        self.sales = self.sales[~bad_dates]

        if self.sales.empty:
            raise ValueError(
                "No rows had a valid date/time after validation. "
                "Please check the CSV file."
            )

        # --- exact duplicate rows ---
        duplicate_rows = self.sales.duplicated()

        if duplicate_rows.any():
            self.warnings.append(
                f"Found {int(duplicate_rows.sum())} exact duplicate "
                "row(s). They were kept — remove them from the export "
                "first if they shouldn't count twice."
            )

        skipped = starting_rows - len(self.sales)

        if skipped:
            self.warnings.insert(
                0,
                f"{skipped} of {starting_rows} row(s) were skipped "
                "during import due to data issues (see below)."
            )

        self.sales["hour"] = (
            self.sales["datetime"].dt.hour
        )

        self.sales["day"] = (
            self.sales["datetime"].dt.day_name()
        )

        self.sales["month"] = (
            self.sales["datetime"].dt.to_period("M")
        )

        self.identify_products()

        return self.sales

    def identify_products(self):
        self.products = (
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

    def organize_products(self):
        if self.products is None:
            self.identify_products()

        count = len(self.products)

        if count == 0:
            return {
                "high": self.products,
                "middle": self.products,
                "low": self.products
            }

        high_end = max(
            1,
            round(count / 3)
        )

        middle_end = max(
            high_end,
            round(count * 2 / 3)
        )

        return {
            "high": self.products.iloc[:high_end],
            "middle": self.products.iloc[
                high_end:middle_end
            ],
            "low": self.products.iloc[
                middle_end:
            ]
        }

    def get_order_items(self):
        return (
            self.sales
            .groupby("order_id")["item"]
            .apply(list)
        )

    def process(self):
        self.read()
        return self.prepare()


if __name__ == "__main__":
    reader = SalesReader("sales.csv")
    sales = reader.process()

    print(sales.head())
