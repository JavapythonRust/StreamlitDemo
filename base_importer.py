import pandas as pd
from pathlib import Path


# Columns every importer must ultimately produce, in this order.
OUTPUT_COLUMNS = [
    "date",
    "time",
    "order_id",
    "item",
    "quantity",
    "price",
]


class BaseImporter:
    """
    Shared behavior for every POS importer.

    A concrete importer (Toast, Square, Shopify, Lightspeed, ...) only
    needs to implement `convert(raw)`, which takes the raw POS
    DataFrame and returns a DataFrame with the six standard Bagelytics
    columns (date, time, order_id, item, quantity, price). Everything
    else — reading the file, finding columns by name, cleaning up
    currency strings, dropping blank rows, and writing the output —
    is handled here so new importers stay small.
    """

    # Human-readable name shown in error messages and the UI.
    display_name = "POS"

    def __init__(self, csv_file):
        self.csv_file = Path(csv_file)

    def read(self):
        if not self.csv_file.exists():
            raise FileNotFoundError(
                f"{self.display_name} CSV not found: {self.csv_file}"
            )

        raw = pd.read_csv(self.csv_file)

        if raw.empty:
            raise ValueError(
                f"The {self.display_name} export has no rows."
            )

        return raw

    @staticmethod
    def find_column(columns, name):
        """
        Find a column by name while ignoring capitalization and
        surrounding whitespace. Returns None if not found.
        """

        for column in columns:
            if str(column).strip().lower() == name.lower():
                return column

        return None

    @classmethod
    def require_columns(cls, columns, names):
        """
        Look up each name in `names` via find_column and raise a
        clear, actionable error listing everything that's missing
        (rather than failing on just the first one).
        """

        found = {name: cls.find_column(columns, name) for name in names}
        missing = [name for name, column in found.items() if column is None]

        if missing:
            raise ValueError(
                f"Missing expected {cls.display_name} column(s): "
                + ", ".join(missing)
                + ". If your export uses different column names, use "
                "'Import from Other POS' instead and map the columns "
                "yourself."
            )

        return found

    @staticmethod
    def clean_currency(series):
        """
        Strip $ signs, commas, and surrounding whitespace so a
        currency-formatted column ('$1,234.50') can be parsed as a
        number. Parentheses (some exports use them for negatives,
        e.g. refunds) are converted to a leading minus sign.
        """

        cleaned = (
            series.astype(str)
            .str.strip()
            .str.replace(r"[,$]", "", regex=True)
            .str.replace(r"^\((.*)\)$", r"-\1", regex=True)
        )

        return pd.to_numeric(cleaned, errors="coerce")

    def convert(self, raw):
        raise NotImplementedError

    def import_sales(self, output_file="sales.csv"):
        raw = self.read()
        sales = self.convert(raw)

        # Drop rows without a usable product name — nothing useful
        # can be reported for a blank item.
        sales = sales[
            sales["item"].notna()
            & (sales["item"].astype(str).str.strip() != "")
        ]

        sales = sales[OUTPUT_COLUMNS]

        if sales.empty:
            raise ValueError(
                f"No usable rows were found in the {self.display_name} "
                "export after removing blank/invalid rows."
            )

        output_path = Path(output_file)
        sales.to_csv(output_path, index=False)

        return output_path
