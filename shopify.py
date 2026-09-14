import pandas as pd

from base_importer import BaseImporter


class ShopifyImporter(BaseImporter):
    """
    Converts a Shopify "Orders" CSV export (Settings/Orders > Export,
    or Orders > Export) into the basic Bagelytics sales.csv format.

    Shopify's export has one row per line item and includes (among
    many others) these documented columns:

        Name, Created at, Lineitem quantity, Lineitem name,
        Lineitem price

    Important real-world quirk: Shopify only fills in order-level
    columns (Name, Created at, etc.) on the FIRST line-item row of
    each order. For an order with 3 items, rows 2 and 3 have blank
    Name/Created at. Naively reading the file would treat those rows
    as having no order/date, so we forward-fill those columns before
    converting. "Lineitem price" is already a per-unit price.

    Bagelytics output:
        date
        time
        order_id
        item
        quantity
        price
    """

    display_name = "Shopify"

    def convert(self, shopify):
        columns = self.require_columns(
            shopify.columns,
            [
                "Name",
                "Created at",
                "Lineitem name",
                "Lineitem quantity",
                "Lineitem price",
            ],
        )

        shopify = shopify.copy()

        # Forward-fill the order-level columns that Shopify leaves
        # blank after the first line of each order.
        shopify[columns["Name"]] = shopify[columns["Name"]].ffill()
        shopify[columns["Created at"]] = (
            shopify[columns["Created at"]].ffill()
        )

        sales = pd.DataFrame()

        sales["order_id"] = shopify[columns["Name"]]
        sales["item"] = shopify[columns["Lineitem name"]]

        sales["quantity"] = pd.to_numeric(
            shopify[columns["Lineitem quantity"]],
            errors="coerce"
        )

        sales["price"] = self.clean_currency(
            shopify[columns["Lineitem price"]]
        )

        datetime = pd.to_datetime(
            shopify[columns["Created at"]],
            errors="coerce",
            utc=False
        )

        sales["date"] = datetime.dt.strftime("%Y-%m-%d")
        sales["time"] = datetime.dt.strftime("%H:%M")

        return sales


if __name__ == "__main__":
    importer = ShopifyImporter("orders_export.csv")
    output = importer.import_sales("sales.csv")
    print(f"Shopify data converted successfully: {output}")
