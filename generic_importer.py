import pandas as pd

from base_importer import BaseImporter


class GenericImporter(BaseImporter):
    """
    Converts an arbitrary POS CSV export into the basic Bagelytics
    sales.csv format using a user-supplied column mapping, rather
    than assuming a fixed set of column names.

    This exists because not every POS's export format is well
    documented or stable (Clover's dashboard reports, for example,
    vary by report type and account). Rather than guessing at column
    names and silently producing wrong data, the caller (typically
    the frontend's "Import from Other POS" dialog) supplies exactly
    which source column maps to which required field.

    `column_map` keys: date, time, order_id, item, quantity, price
    `column_map` values: the exact column name in the source CSV.

    `date` and `time` may point to the SAME column if the source
    file stores a single combined date/time value.

    Bagelytics output:
        date
        time
        order_id
        item
        quantity
        price
    """

    display_name = "Other POS"

    REQUIRED_KEYS = ["date", "time", "order_id", "item", "quantity", "price"]

    def __init__(self, csv_file, column_map):
        super().__init__(csv_file)

        missing_keys = [k for k in self.REQUIRED_KEYS if k not in column_map]

        if missing_keys:
            raise ValueError(
                "Column mapping is missing: " + ", ".join(missing_keys)
            )

        self.column_map = column_map

    def convert(self, raw):
        for field, source_column in self.column_map.items():
            if source_column not in raw.columns:
                raise ValueError(
                    f"Column '{source_column}' (mapped to '{field}') "
                    "was not found in the CSV file."
                )

        sales = pd.DataFrame()

        sales["order_id"] = raw[self.column_map["order_id"]]
        sales["item"] = raw[self.column_map["item"]]

        sales["quantity"] = pd.to_numeric(
            raw[self.column_map["quantity"]],
            errors="coerce"
        )

        sales["price"] = self.clean_currency(
            raw[self.column_map["price"]]
        )

        same_column = (
            self.column_map["date"] == self.column_map["time"]
        )

        if same_column:
            combined = pd.to_datetime(
                raw[self.column_map["date"]],
                errors="coerce"
            )
        else:
            combined = pd.to_datetime(
                raw[self.column_map["date"]].astype(str)
                + " "
                + raw[self.column_map["time"]].astype(str),
                errors="coerce"
            )

        sales["date"] = combined.dt.strftime("%Y-%m-%d")
        sales["time"] = combined.dt.strftime("%H:%M")

        return sales
