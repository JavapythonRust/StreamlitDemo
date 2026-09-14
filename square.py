import pandas as pd

from base_importer import BaseImporter


class SquareImporter(BaseImporter):
    """
    Converts a Square "Transactions" item-detail CSV export into the
    basic Bagelytics sales.csv format.

    In Square Dashboard: Reports > Transactions > Export, or
    Reports > Custom > Custom Item report > Export. The item-level
    export has one row per item sold and includes these columns
    (verified against real Square exports):

        Date, Time, Time Zone, Category, Item, Qty, Price Point Name,
        SKU, Modifiers Applied, Gross Sales, Discounts, Net Sales,
        Tax, Transaction ID, Payment ID, Device Name, Notes, Details,
        Event Type, Location, Dining Option, Customer ID,
        Customer Name, Customer Reference ID, Unit, Count

    Only Date, Time, Item, Qty, Gross Sales, and Transaction ID are
    used. Gross Sales is the line total (already Qty x unit price),
    so the per-unit price is derived by dividing it back out.

    Bagelytics output:
        date
        time
        order_id
        item
        quantity
        price
    """

    display_name = "Square"

    def convert(self, square):
        columns = self.require_columns(
            square.columns,
            ["Date", "Time", "Item", "Qty", "Gross Sales", "Transaction ID"],
        )

        sales = pd.DataFrame()

        sales["order_id"] = square[columns["Transaction ID"]]
        sales["item"] = square[columns["Item"]]

        sales["quantity"] = pd.to_numeric(
            square[columns["Qty"]],
            errors="coerce"
        )

        gross_sales = self.clean_currency(square[columns["Gross Sales"]])

        # Square's "Gross Sales" is the line total, not the unit
        # price — Bagelytics stores a per-unit price, so divide back
        # out by quantity. Guard against zero/blank quantity.
        safe_quantity = sales["quantity"].replace(0, pd.NA)
        sales["price"] = gross_sales / safe_quantity

        dates = pd.to_datetime(
            square[columns["Date"]],
            errors="coerce"
        )

        sales["date"] = dates.dt.strftime("%Y-%m-%d")

        # Time is exported separately (e.g. "8:32 AM") rather than
        # combined with the date.
        times = pd.to_datetime(
            square[columns["Time"]].astype(str),
            errors="coerce",
            format="mixed"
        )

        sales["time"] = times.dt.strftime("%H:%M")

        return sales


if __name__ == "__main__":
    importer = SquareImporter("items-2026-09-01-2026-09-30.csv")
    output = importer.import_sales("sales.csv")
    print(f"Square data converted successfully: {output}")
