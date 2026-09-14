import pandas as pd

from base_importer import BaseImporter


class ToastImporter(BaseImporter):
    """
    Converts a Toast ItemSelectionDetails.csv
    into the basic Bagelytics sales.csv format.

    Toast fields used:
        Order Id
        Order Date
        Menu Item
        Qty
        Gross Price

    Bagelytics output:
        date
        time
        order_id
        item
        quantity
        price
    """

    display_name = "Toast"

    def convert(self, toast):
        columns = self.require_columns(
            toast.columns,
            ["Order Id", "Order Date", "Menu Item", "Qty", "Gross Price"],
        )

        sales = pd.DataFrame()

        sales["order_id"] = toast[columns["Order Id"]]
        sales["item"] = toast[columns["Menu Item"]]

        sales["quantity"] = pd.to_numeric(
            toast[columns["Qty"]],
            errors="coerce"
        )

        sales["price"] = pd.to_numeric(
            toast[columns["Gross Price"]],
            errors="coerce"
        )

        datetime = pd.to_datetime(
            toast[columns["Order Date"]],
            errors="coerce"
        )

        sales["date"] = datetime.dt.strftime("%Y-%m-%d")
        sales["time"] = datetime.dt.strftime("%H:%M")

        return sales


if __name__ == "__main__":
    importer = ToastImporter("ItemSelectionDetails.csv")
    output = importer.import_sales("sales.csv")
    print(f"Toast data converted successfully: {output}")
