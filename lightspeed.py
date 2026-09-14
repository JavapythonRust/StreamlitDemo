import pandas as pd

from base_importer import BaseImporter


class LightspeedImporter(BaseImporter):
    """
    Converts a Lightspeed Retail "Sales Listings - Transaction Line"
    CSV export into the basic Bagelytics sales.csv format.

    In Lightspeed: Reports > Sales & Refunds > Lines > Export. That
    export (internally named reports_sales_listings_transaction_line)
    has one row per item sold and includes these documented columns:

        ID, Date, Description, Qty, Retail, Subtotal, Discount, Tax,
        Customer, Source

    ID is the sale/transaction identifier (shared by every line of
    the same sale), Description is the item name, and Retail is the
    per-unit retail price.

    Bagelytics output:
        date
        time
        order_id
        item
        quantity
        price
    """

    display_name = "Lightspeed"

    def convert(self, lightspeed):
        columns = self.require_columns(
            lightspeed.columns,
            ["ID", "Date", "Description", "Qty", "Retail"],
        )

        sales = pd.DataFrame()

        sales["order_id"] = lightspeed[columns["ID"]]
        sales["item"] = lightspeed[columns["Description"]]

        sales["quantity"] = pd.to_numeric(
            lightspeed[columns["Qty"]],
            errors="coerce"
        )

        sales["price"] = self.clean_currency(
            lightspeed[columns["Retail"]]
        )

        datetime = pd.to_datetime(
            lightspeed[columns["Date"]],
            errors="coerce"
        )

        sales["date"] = datetime.dt.strftime("%Y-%m-%d")
        sales["time"] = datetime.dt.strftime("%H:%M")

        return sales


if __name__ == "__main__":
    importer = LightspeedImporter("reports_sales_listings_transaction_line.csv")
    output = importer.import_sales("sales.csv")
    print(f"Lightspeed data converted successfully: {output}")
