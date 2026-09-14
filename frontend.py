
import os
import subprocess
import tempfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

import pandas as pd

from read import SalesReader
from analytics import Analytics
from graph import Grapher
from toast import ToastImporter
from square import SquareImporter
from shopify import ShopifyImporter
from lightspeed import LightspeedImporter
from generic_importer import GenericImporter


IMPORTERS = {
    "toast": ToastImporter,
    "square": SquareImporter,
    "shopify": ShopifyImporter,
    "lightspeed": LightspeedImporter,
}


class BagelyticsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bagelytics")

        # Slightly larger default window
        self.root.geometry("1250x800")
        self.root.minsize(1050, 700)

        # =====================================================
        # COLOR SCHEME
        # =====================================================

        self.colors = {
            "bg": "#F8FAFC",
            "card": "#FFFFFF",
            "primary": "#2563EB",
            "primary_hover": "#1D4ED8",
            "text": "#0F172A",
            "secondary_text": "#64748B",
            "border": "#E2E8F0",
            "success": "#16A34A",
            "warning": "#D97706",
            "danger": "#DC2626",
        }

        self.sales = None
        self.sales_all = None
        self.reader = None
        self.analytics = None
        self.grapher = None
        self.graph_paths = []

        self.apply_theme()

        self.create_menu()
        self.create_filter_bar()
        self.create_notebook()

    # =========================================================
    # THEME
    # =========================================================

    def apply_theme(self):
        style = ttk.Style()

        style.theme_use("clam")

        bg = self.colors["bg"]
        card = self.colors["card"]
        primary = self.colors["primary"]
        text = self.colors["text"]
        secondary = self.colors["secondary_text"]
        border = self.colors["border"]

        self.root.configure(
            background=bg
        )

        # -----------------------------------------------------
        # Frames
        # -----------------------------------------------------

        style.configure(
            "TFrame",
            background=bg
        )

        style.configure(
            "Card.TFrame",
            background=card
        )

        # -----------------------------------------------------
        # Labels
        # -----------------------------------------------------

        style.configure(
            "TLabel",
            background=bg,
            foreground=text,
            font=("Arial", 12)
        )

        style.configure(
            "Secondary.TLabel",
            background=bg,
            foreground=secondary,
            font=("Arial", 11)
        )

        # -----------------------------------------------------
        # Label Frames
        # -----------------------------------------------------

        style.configure(
            "TLabelframe",
            background=card,
            foreground=text,
            bordercolor=border,
            relief="solid"
        )

        style.configure(
            "TLabelframe.Label",
            background=card,
            foreground=text,
            font=("Arial", 12, "bold")
        )

        # -----------------------------------------------------
        # Buttons
        # -----------------------------------------------------

        style.configure(
            "TButton",
            background=card,
            foreground=text,
            bordercolor=border,
            padding=(15, 9),
            font=("Arial", 12)
        )

        style.map(
            "TButton",
            background=[
                ("active", primary),
                ("pressed", self.colors["primary_hover"])
            ],
            foreground=[
                ("active", "#FFFFFF"),
                ("pressed", "#FFFFFF")
            ]
        )

        # -----------------------------------------------------
        # Entries
        # -----------------------------------------------------

        style.configure(
            "TEntry",
            fieldbackground=card,
            foreground=text,
            bordercolor=border,
            padding=8,
            font=("Arial", 12)
        )

        # -----------------------------------------------------
        # Combobox
        # -----------------------------------------------------

        style.configure(
            "TCombobox",
            fieldbackground=card,
            background=card,
            foreground=text,
            bordercolor=border,
            padding=7,
            font=("Arial", 12)
        )

        # -----------------------------------------------------
        # Notebook / Tabs
        # -----------------------------------------------------

        style.configure(
            "TNotebook",
            background=bg,
            borderwidth=0
        )

        style.configure(
            "TNotebook.Tab",
            background=bg,
            foreground=secondary,
            padding=(19, 12),
            font=("Arial", 12)
        )

        style.map(
            "TNotebook.Tab",
            background=[
                ("selected", card)
            ],
            foreground=[
                ("selected", primary)
            ]
        )

        # -----------------------------------------------------
        # Treeview
        # -----------------------------------------------------

        style.configure(
            "Treeview",
            background=card,
            fieldbackground=card,
            foreground=text,
            bordercolor=border,
            rowheight=36,
            font=("Arial", 12)
        )

        style.configure(
            "Treeview.Heading",
            background=bg,
            foreground=text,
            bordercolor=border,
            font=("Arial", 12, "bold"),
            padding=10
        )

        style.map(
            "Treeview",
            background=[
                ("selected", primary)
            ],
            foreground=[
                ("selected", "#FFFFFF")
            ]
        )

        # -----------------------------------------------------
        # Scrollbars
        # -----------------------------------------------------

        style.configure(
            "Vertical.TScrollbar",
            background=bg,
            troughcolor=bg,
            bordercolor=bg
        )

        style.configure(
            "Horizontal.TScrollbar",
            background=bg,
            troughcolor=bg,
            bordercolor=bg
        )

    # =========================================================
    # MENU
    # =========================================================

    def create_menu(self):
        menu = tk.Menu(
            self.root,
            tearoff=0,
            bg=self.colors["card"],
            fg=self.colors["text"],
            activebackground=self.colors["primary"],
            activeforeground="#FFFFFF",
            font=("Arial", 12)
        )

        file_menu = tk.Menu(
            menu,
            tearoff=0,
            bg=self.colors["card"],
            fg=self.colors["text"],
            activebackground=self.colors["primary"],
            activeforeground="#FFFFFF",
            font=("Arial", 12)
        )

        file_menu.add_command(
            label="Open Sales CSV",
            command=self.load_csv
        )

        import_menu = tk.Menu(
            file_menu,
            tearoff=0,
            bg=self.colors["card"],
            fg=self.colors["text"],
            activebackground=self.colors["primary"],
            activeforeground="#FFFFFF",
            font=("Arial", 12)
        )

        import_menu.add_command(
            label="Toast (ItemSelectionDetails.csv)",
            command=lambda: self.run_importer(
                "toast",
                "ItemSelectionDetails CSV"
            )
        )

        import_menu.add_command(
            label="Square (Transactions/Items CSV)",
            command=lambda: self.run_importer(
                "square",
                "Square Transactions CSV"
            )
        )

        import_menu.add_command(
            label="Shopify (Orders export CSV)",
            command=lambda: self.run_importer(
                "shopify",
                "Shopify Orders CSV"
            )
        )

        import_menu.add_command(
            label="Lightspeed (Transaction Lines CSV)",
            command=lambda: self.run_importer(
                "lightspeed",
                "Lightspeed Transaction Lines CSV"
            )
        )

        import_menu.add_separator()

        import_menu.add_command(
            label="Other POS (choose columns)...",
            command=self.run_generic_importer
        )

        file_menu.add_cascade(
            label="Import From POS",
            menu=import_menu
        )

        file_menu.add_separator()

        file_menu.add_command(
            label="Exit",
            command=self.root.destroy
        )

        menu.add_cascade(
            label="File",
            menu=file_menu
        )

        self.root.config(
            menu=menu
        )

    # =========================================================
    # DATE FILTER BAR
    # =========================================================

    def create_filter_bar(self):
        self.filter_frame = ttk.Frame(
            self.root
        )

        self.filter_frame.pack(
            fill="x",
            padx=14,
            pady=(14, 0)
        )

        ttk.Label(
            self.filter_frame,
            text="Date range:"
        ).pack(
            side="left",
            padx=(0, 7)
        )

        ttk.Label(
            self.filter_frame,
            text="From"
        ).pack(
            side="left"
        )

        self.filter_from = ttk.Entry(
            self.filter_frame,
            width=14
        )

        self.filter_from.pack(
            side="left",
            padx=(4, 12)
        )

        ttk.Label(
            self.filter_frame,
            text="To"
        ).pack(
            side="left"
        )

        self.filter_to = ttk.Entry(
            self.filter_frame,
            width=14
        )

        self.filter_to.pack(
            side="left",
            padx=(4, 12)
        )

        ttk.Label(
            self.filter_frame,
            text="(YYYY-MM-DD)",
            foreground=self.colors["secondary_text"]
        ).pack(
            side="left",
            padx=(0, 12)
        )

        ttk.Button(
            self.filter_frame,
            text="Apply Filter",
            command=self.apply_filter
        ).pack(
            side="left",
            padx=(0, 7)
        )

        ttk.Button(
            self.filter_frame,
            text="Clear Filter",
            command=self.clear_filter
        ).pack(
            side="left"
        )

        self.filter_status_label = ttk.Label(
            self.filter_frame,
            text="Load a CSV to begin.",
            foreground=self.colors["secondary_text"]
        )

        self.filter_status_label.pack(
            side="left",
            padx=(18, 0)
        )

    def apply_filter(self):
        if self.sales_all is None:
            messagebox.showwarning(
                "Bagelytics",
                "Load sales data first."
            )

            return

        from_text = self.filter_from.get().strip()
        to_text = self.filter_to.get().strip()

        filtered = self.sales_all

        try:
            if from_text:
                filtered = filtered[
                    filtered["datetime"].dt.date
                    >= pd.to_datetime(from_text).date()
                ]

            if to_text:
                filtered = filtered[
                    filtered["datetime"].dt.date
                    <= pd.to_datetime(to_text).date()
                ]

        except (ValueError, TypeError):
            messagebox.showerror(
                "Bagelytics",
                "Could not understand that date. "
                "Please use the YYYY-MM-DD format."
            )

            return

        if filtered.empty:
            messagebox.showwarning(
                "Bagelytics",
                "No rows fall within that date range. "
                "The filter was not applied."
            )

            return

        self.refresh_from_sales(
            filtered.copy()
        )

        self.filter_status_label.config(
            text=(
                f"Showing {len(filtered):,} of "
                f"{len(self.sales_all):,} rows."
            )
        )

    def clear_filter(self):
        self.filter_from.delete(
            0,
            tk.END
        )

        self.filter_to.delete(
            0,
            tk.END
        )

        if self.sales_all is None:
            return

        self.refresh_from_sales(
            self.sales_all.copy()
        )

        self.filter_status_label.config(
            text=(
                f"Showing all "
                f"{len(self.sales_all):,} rows."
            )
        )

    # =========================================================
    # NOTEBOOK / TABS
    # =========================================================

    def create_notebook(self):
        self.notebook = ttk.Notebook(
            self.root
        )

        self.notebook.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=14
        )

        self.create_dashboard_tab()
        self.create_products_tab()
        self.create_performance_tab()
        self.create_bundle_tab()
        self.create_day_parts_tab()
        self.create_patterns_tab()
        self.create_graphs_tab()

    # =========================================================
    # DASHBOARD
    # =========================================================

    def create_dashboard_tab(self):
        self.dashboard_tab = ttk.Frame(
            self.notebook
        )

        self.notebook.add(
            self.dashboard_tab,
            text="Dashboard"
        )

        metrics_frame = ttk.Frame(
            self.dashboard_tab
        )

        metrics_frame.pack(
            fill="x",
            padx=24,
            pady=24
        )

        self.revenue_label = self.create_metric(
            metrics_frame,
            "Total Revenue",
            0
        )

        self.items_label = self.create_metric(
            metrics_frame,
            "Items Sold",
            1
        )

        self.orders_label = self.create_metric(
            metrics_frame,
            "Orders",
            2
        )

        self.aov_label = self.create_metric(
            metrics_frame,
            "Average Order",
            3
        )

        insights_frame = ttk.LabelFrame(
            self.dashboard_tab,
            text="Key Insights"
        )

        insights_frame.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=12
        )

        self.insights_text = tk.Text(
            insights_frame,
            height=15,
            wrap="word",
            state="disabled",
            background=self.colors["card"],
            foreground=self.colors["text"],
            insertbackground=self.colors["text"],
            selectbackground=self.colors["primary"],
            selectforeground="#FFFFFF",
            relief="flat",
            borderwidth=0,
            font=("Arial", 12),
            padx=14,
            pady=14
        )

        self.insights_text.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=12
        )

    def create_metric(
        self,
        parent,
        title,
        column
    ):
        frame = ttk.LabelFrame(
            parent,
            text=title
        )

        frame.grid(
            row=0,
            column=column,
            padx=10,
            sticky="nsew"
        )

        parent.columnconfigure(
            column,
            weight=1
        )

        label = tk.Label(
            frame,
            text="--",
            bg=self.colors["card"],
            fg=self.colors["primary"],
            font=("Arial", 26, "bold")
        )

        label.pack(
            padx=35,
            pady=28
        )

        return label

    # =========================================================
    # PRODUCTS
    # =========================================================

    def create_products_tab(self):
        self.products_tab = ttk.Frame(
            self.notebook
        )

        self.notebook.add(
            self.products_tab,
            text="Products"
        )

        self.products_tree = ttk.Treeview(
            self.products_tab,
            columns=(
                "product",
                "quantity",
                "revenue"
            ),
            show="headings"
        )

        self.products_tree.heading(
            "product",
            text="Product"
        )

        self.products_tree.heading(
            "quantity",
            text="Quantity Sold"
        )

        self.products_tree.heading(
            "revenue",
            text="Revenue"
        )

        self.products_tree.column(
            "product",
            width=450
        )

        self.products_tree.column(
            "quantity",
            width=180
        )

        self.products_tree.column(
            "revenue",
            width=180
        )

        self.products_tree.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=14
        )

    # =========================================================
    # PRODUCT PERFORMANCE
    # =========================================================

    def create_performance_tab(self):
        self.performance_tab = ttk.Frame(
            self.notebook
        )

        self.notebook.add(
            self.performance_tab,
            text="Product Performance"
        )

        explanation = ttk.Label(
            self.performance_tab,
            text=(
                "Products are grouped by whether their volume and "
                "revenue are above or below the median product's. "
                "'High volume / Low revenue' items may deserve a "
                "price look; 'Low volume / Low revenue' items may "
                "be worth reviewing or replacing."
            ),
            wraplength=1100,
            justify="left"
        )

        explanation.pack(
            fill="x",
            padx=20,
            pady=(20, 8)
        )

        self.performance_tree = ttk.Treeview(
            self.performance_tab,
            columns=(
                "product",
                "quantity",
                "revenue",
                "quadrant"
            ),
            show="headings"
        )

        self.performance_tree.heading(
            "product",
            text="Product"
        )

        self.performance_tree.heading(
            "quantity",
            text="Quantity Sold"
        )

        self.performance_tree.heading(
            "revenue",
            text="Revenue"
        )

        self.performance_tree.heading(
            "quadrant",
            text="Category"
        )

        self.performance_tree.column(
            "product",
            width=400
        )

        self.performance_tree.column(
            "quantity",
            width=170
        )

        self.performance_tree.column(
            "revenue",
            width=170
        )

        self.performance_tree.column(
            "quadrant",
            width=300
        )

        self.performance_tree.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=14
        )

    # =========================================================
    # BUNDLES
    # =========================================================

    def create_bundle_tab(self):
        self.bundle_tab = ttk.Frame(
            self.notebook
        )

        self.notebook.add(
            self.bundle_tab,
            text="Bundle Opportunities"
        )

        self.bundle_tree = ttk.Treeview(
            self.bundle_tab,
            columns=(
                "item_1",
                "item_2",
                "orders",
                "opportunity"
            ),
            show="headings"
        )

        self.bundle_tree.heading(
            "item_1",
            text="Product 1"
        )

        self.bundle_tree.heading(
            "item_2",
            text="Product 2"
        )

        self.bundle_tree.heading(
            "orders",
            text="Orders Together"
        )

        self.bundle_tree.heading(
            "opportunity",
            text="Opportunity"
        )

        self.bundle_tree.column(
            "item_1",
            width=300
        )

        self.bundle_tree.column(
            "item_2",
            width=300
        )

        self.bundle_tree.column(
            "orders",
            width=180
        )

        self.bundle_tree.column(
            "opportunity",
            width=350
        )

        self.bundle_tree.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=14
        )

    # =========================================================
    # DAY PARTS
    # =========================================================

    def create_day_parts_tab(self):
        self.day_parts_tab = ttk.Frame(
            self.notebook
        )

        self.notebook.add(
            self.day_parts_tab,
            text="Day Parts"
        )

        self.day_parts_tree = ttk.Treeview(
            self.day_parts_tab,
            columns=(
                "day_part",
                "revenue",
                "orders",
                "items",
                "average_order",
                "popular_product"
            ),
            show="headings"
        )

        self.day_parts_tree.heading(
            "day_part",
            text="Day Part"
        )

        self.day_parts_tree.heading(
            "revenue",
            text="Revenue"
        )

        self.day_parts_tree.heading(
            "orders",
            text="Orders"
        )

        self.day_parts_tree.heading(
            "items",
            text="Items Sold"
        )

        self.day_parts_tree.heading(
            "average_order",
            text="Avg Order"
        )

        self.day_parts_tree.heading(
            "popular_product",
            text="Most Popular Product"
        )

        self.day_parts_tree.column(
            "day_part",
            width=180
        )

        self.day_parts_tree.column(
            "revenue",
            width=150
        )

        self.day_parts_tree.column(
            "orders",
            width=120
        )

        self.day_parts_tree.column(
            "items",
            width=150
        )

        self.day_parts_tree.column(
            "average_order",
            width=150
        )

        self.day_parts_tree.column(
            "popular_product",
            width=350
        )

        self.day_parts_tree.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=14
        )

    # =========================================================
    # PATTERNS
    # =========================================================

    def create_patterns_tab(self):
        self.patterns_tab = ttk.Frame(
            self.notebook
        )

        self.notebook.add(
            self.patterns_tab,
            text="Patterns"
        )

        explanation = ttk.Label(
            self.patterns_tab,
            text=(
                "Automatically detected relationships between products. "
                "Patterns can come from sales moving together over time "
                "or products appearing together in orders."
            ),
            wraplength=1100,
            justify="left"
        )

        explanation.pack(
            fill="x",
            padx=20,
            pady=(20, 8)
        )

        tree_frame = ttk.Frame(
            self.patterns_tab
        )

        tree_frame.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=14
        )

        self.patterns_tree = ttk.Treeview(
            tree_frame,
            columns=(
                "type",
                "item_1",
                "item_2",
                "strength",
                "description"
            ),
            show="headings"
        )

        self.patterns_tree.heading(
            "type",
            text="Type"
        )

        self.patterns_tree.heading(
            "item_1",
            text="Item 1"
        )

        self.patterns_tree.heading(
            "item_2",
            text="Item 2"
        )

        self.patterns_tree.heading(
            "strength",
            text="Strength"
        )

        self.patterns_tree.heading(
            "description",
            text="Pattern"
        )

        self.patterns_tree.column(
            "type",
            width=190,
            anchor="w"
        )

        self.patterns_tree.column(
            "item_1",
            width=250,
            anchor="w"
        )

        self.patterns_tree.column(
            "item_2",
            width=250,
            anchor="w"
        )

        self.patterns_tree.column(
            "strength",
            width=130,
            anchor="center"
        )

        self.patterns_tree.column(
            "description",
            width=600,
            anchor="w"
        )

        scrollbar = ttk.Scrollbar(
            tree_frame,
            orient="vertical",
            command=self.patterns_tree.yview
        )

        self.patterns_tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.patterns_tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

    # =========================================================
    # GRAPHS
    # =========================================================

    def create_graphs_tab(self):
        self.graphs_tab = ttk.Frame(
            self.notebook
        )

        self.notebook.add(
            self.graphs_tab,
            text="Graphs"
        )

        self.graphs_listbox = tk.Listbox(
            self.graphs_tab,
            background=self.colors["card"],
            foreground=self.colors["text"],
            selectbackground=self.colors["primary"],
            selectforeground="#FFFFFF",
            highlightbackground=self.colors["border"],
            highlightcolor=self.colors["primary"],
            relief="solid",
            borderwidth=1,
            font=("Arial", 12),
            activestyle="none"
        )

        self.graphs_listbox.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=14
        )

        self.open_graph_button = ttk.Button(
            self.graphs_tab,
            text="Open Selected Graph",
            command=self.open_selected_graph
        )

        self.open_graph_button.pack(
            pady=(0, 14)
        )

    # =========================================================
    # LOAD CSV
    # =========================================================

    def load_csv(self):
        csv_file = filedialog.askopenfilename(
            title="Select Sales CSV",
            filetypes=[
                (
                    "CSV files",
                    "*.csv"
                ),
                (
                    "All files",
                    "*.*"
                )
            ]
        )

        if not csv_file:
            return

        try:
            self.reader = SalesReader(
                csv_file
            )

            sales = self.reader.process()

            self.sales_all = sales

            self.refresh_from_sales(
                sales
            )

            self.clear_filter_fields_only()

            self.report_load_result()

        except Exception as error:
            messagebox.showerror(
                "Error",
                f"Could not load sales data:\n\n{error}"
            )

    def clear_filter_fields_only(self):
        self.filter_from.delete(
            0,
            tk.END
        )

        self.filter_to.delete(
            0,
            tk.END
        )

        if self.sales_all is not None:
            self.filter_status_label.config(
                text=(
                    f"Showing all "
                    f"{len(self.sales_all):,} rows."
                )
            )

    def report_load_result(self):
        warnings = getattr(
            self.reader,
            "warnings",
            []
        )

        if warnings:
            messagebox.showwarning(
                "Bagelytics — Data Quality",
                "Sales data loaded, but some issues were found:\n\n"
                + "\n".join(
                    f"• {warning}"
                    for warning in warnings
                )
            )
        else:
            messagebox.showinfo(
                "Bagelytics",
                "Sales data loaded successfully."
            )

    def refresh_from_sales(self, sales):
        """
        Runs analytics + graphing on the given prepared
        sales DataFrame and refreshes every tab.
        """

        self.sales = sales

        self.analytics = Analytics(
            self.sales
        )

        summary = self.analytics.summary()

        self.grapher = Grapher(
            self.sales
        )

        graph_paths = self.grapher.generate_all()

        self.update_dashboard(
            summary
        )

        self.update_products()

        self.update_performance(
            summary.get(
                "product_performance_matrix"
            )
        )

        self.update_bundles(
            summary.get(
                "bundle_opportunities"
            )
        )

        self.update_day_parts(
            summary.get(
                "day_part_analysis"
            )
        )

        self.update_patterns(
            summary.get(
                "patterns"
            )
        )

        self.update_graphs(
            graph_paths
        )

    # =========================================================
    # IMPORT FROM POS
    # =========================================================

    def run_importer(
        self,
        importer_key,
        file_description
    ):
        importer_class = IMPORTERS[
            importer_key
        ]

        csv_file = filedialog.askopenfilename(
            title=f"Select {file_description}",
            filetypes=[
                (
                    "CSV files",
                    "*.csv"
                ),
                (
                    "All files",
                    "*.*"
                )
            ]
        )

        if not csv_file:
            return

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                converted_path = (
                    Path(temp_dir)
                    / "sales.csv"
                )

                importer = importer_class(
                    csv_file
                )

                importer.import_sales(
                    converted_path
                )

                self.reader = SalesReader(
                    converted_path
                )

                sales = self.reader.process()

            self.sales_all = sales

            self.refresh_from_sales(
                sales
            )

            self.clear_filter_fields_only()

            self.report_load_result()

        except Exception as error:
            messagebox.showerror(
                "Error",
                (
                    f"Could not import "
                    f"{file_description}:\n\n"
                    f"{error}"
                )
            )

    def run_generic_importer(self):
        csv_file = filedialog.askopenfilename(
            title="Select POS Export CSV",
            filetypes=[
                (
                    "CSV files",
                    "*.csv"
                ),
                (
                    "All files",
                    "*.*"
                )
            ]
        )

        if not csv_file:
            return

        try:
            columns = list(
                pd.read_csv(
                    csv_file,
                    nrows=0
                ).columns
            )

        except Exception as error:
            messagebox.showerror(
                "Error",
                f"Could not read that CSV file:\n\n{error}"
            )

            return

        mapping = self.prompt_column_mapping(
            columns
        )

        if mapping is None:
            return

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                converted_path = (
                    Path(temp_dir)
                    / "sales.csv"
                )

                importer = GenericImporter(
                    csv_file,
                    mapping
                )

                importer.import_sales(
                    converted_path
                )

                self.reader = SalesReader(
                    converted_path
                )

                sales = self.reader.process()

            self.sales_all = sales

            self.refresh_from_sales(
                sales
            )

            self.clear_filter_fields_only()

            self.report_load_result()

        except Exception as error:
            messagebox.showerror(
                "Error",
                f"Could not import that file:\n\n{error}"
            )

    def prompt_column_mapping(
        self,
        columns
    ):
        """
        Small modal dialog letting the user pick which
        CSV column corresponds to each Bagelytics field.
        """

        dialog = tk.Toplevel(
            self.root
        )

        dialog.title(
            "Map CSV Columns"
        )

        dialog.geometry(
            "560x440"
        )

        dialog.configure(
            background=self.colors["bg"]
        )

        dialog.transient(
            self.root
        )

        dialog.grab_set()

        ttk.Label(
            dialog,
            text=(
                "Match each Bagelytics field to the "
                "matching column in your CSV file."
            ),
            wraplength=500,
            justify="left"
        ).pack(
            padx=20,
            pady=(20, 12),
            anchor="w"
        )

        fields = [
            (
                "date",
                "Date"
            ),
            (
                "time",
                "Time (pick same column as Date if combined)"
            ),
            (
                "order_id",
                "Order / Transaction ID"
            ),
            (
                "item",
                "Item / Product Name"
            ),
            (
                "quantity",
                "Quantity"
            ),
            (
                "price",
                "Unit Price"
            ),
        ]

        selections = {}

        form = ttk.Frame(
            dialog
        )

        form.pack(
            fill="both",
            expand=True,
            padx=20
        )

        for row, (key, label) in enumerate(fields):
            ttk.Label(
                form,
                text=label
            ).grid(
                row=row,
                column=0,
                sticky="w",
                pady=8
            )

            combo = ttk.Combobox(
                form,
                values=columns,
                state="readonly",
                width=34
            )

            if columns:
                combo.set(
                    columns[0]
                )

            combo.grid(
                row=row,
                column=1,
                sticky="e",
                pady=8
            )

            selections[key] = combo

        result = {
            "mapping": None
        }

        def on_ok():
            result["mapping"] = {
                key: combo.get()
                for key, combo in selections.items()
            }

            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        button_frame = ttk.Frame(
            dialog
        )

        button_frame.pack(
            pady=18
        )

        ttk.Button(
            button_frame,
            text="Import",
            command=on_ok
        ).pack(
            side="left",
            padx=7
        )

        ttk.Button(
            button_frame,
            text="Cancel",
            command=on_cancel
        ).pack(
            side="left",
            padx=7
        )

        self.root.wait_window(
            dialog
        )

        return result["mapping"]

    # =========================================================
    # UPDATE DASHBOARD
    # =========================================================

    def update_dashboard(
        self,
        summary
    ):
        total_revenue = summary.get(
            "total_revenue",
            0
        )

        total_items = summary.get(
            "total_items_sold",
            0
        )

        total_orders = summary.get(
            "total_orders",
            0
        )

        average_order = summary.get(
            "average_order_value",
            0
        )

        self.revenue_label.config(
            text=f"${total_revenue:,.2f}"
        )

        self.items_label.config(
            text=f"{total_items:,.0f}"
        )

        self.orders_label.config(
            text=f"{total_orders:,.0f}"
        )

        self.aov_label.config(
            text=f"${average_order:,.2f}"
        )

        insights = []

        best_product = summary.get(
            "best_selling_product"
        )

        highest_revenue = summary.get(
            "highest_revenue_product"
        )

        lowest_revenue = summary.get(
            "lowest_revenue_product"
        )

        busiest_hour = summary.get(
            "busiest_hour"
        )

        busiest_day = summary.get(
            "busiest_day"
        )

        least_busy_day = summary.get(
            "least_busy_day"
        )

        if best_product:
            insights.append(
                f"Best-selling product: {best_product}"
            )

        if highest_revenue:
            insights.append(
                f"Highest-revenue product: "
                f"{highest_revenue}"
            )

        if lowest_revenue:
            insights.append(
                f"Lowest-revenue product: "
                f"{lowest_revenue}"
            )

        if busiest_hour is not None:
            insights.append(
                f"Busiest hour: {busiest_hour}"
            )

        if busiest_day:
            insights.append(
                f"Busiest day: {busiest_day}"
            )

        if least_busy_day:
            insights.append(
                f"Least busy day: {least_busy_day}"
            )

        self.insights_text.config(
            state="normal"
        )

        self.insights_text.delete(
            "1.0",
            tk.END
        )

        if insights:
            self.insights_text.insert(
                tk.END,
                "\n".join(insights)
            )
        else:
            self.insights_text.insert(
                tk.END,
                "No insights available."
            )

        self.insights_text.config(
            state="disabled"
        )

    # =========================================================
    # UPDATE PRODUCTS
    # =========================================================

    def update_products(self):
        for row in self.products_tree.get_children():
            self.products_tree.delete(
                row
            )

        if self.analytics is None:
            return

        products = self.analytics.product_sales()

        if products is None or products.empty:
            return

        for product, row in products.iterrows():
            self.products_tree.insert(
                "",
                "end",
                values=(
                    product,
                    int(
                        row["quantity_sold"]
                    ),
                    f"${row['revenue']:,.2f}"
                )
            )

    # =========================================================
    # UPDATE PRODUCT PERFORMANCE
    # =========================================================

    def update_performance(
        self,
        matrix
    ):
        for row in self.performance_tree.get_children():
            self.performance_tree.delete(
                row
            )

        if matrix is None or matrix.empty:
            return

        for product, row in matrix.iterrows():
            self.performance_tree.insert(
                "",
                "end",
                values=(
                    product,
                    int(
                        row["quantity_sold"]
                    ),
                    f"${row['revenue']:,.2f}",
                    row["quadrant"]
                )
            )

    # =========================================================
    # UPDATE BUNDLES
    # =========================================================

    def update_bundles(
        self,
        bundles
    ):
        for row in self.bundle_tree.get_children():
            self.bundle_tree.delete(
                row
            )

        if bundles is None:
            return

        for bundle in bundles:
            if not isinstance(
                bundle,
                dict
            ):
                continue

            item_1 = bundle.get(
                "item_1",
                ""
            )

            item_2 = bundle.get(
                "item_2",
                ""
            )

            orders = bundle.get(
                "orders_together",
                bundle.get(
                    "count",
                    0
                )
            )

            opportunity = bundle.get(
                "opportunity",
                "Consider bundling these products."
            )

            self.bundle_tree.insert(
                "",
                "end",
                values=(
                    item_1,
                    item_2,
                    orders,
                    opportunity
                )
            )

    # =========================================================
    # UPDATE DAY PARTS
    # =========================================================

    def update_day_parts(
        self,
        day_parts
    ):
        for row in self.day_parts_tree.get_children():
            self.day_parts_tree.delete(
                row
            )

        if day_parts is None:
            return

        if hasattr(
            day_parts,
            "iterrows"
        ):
            for day_part, row in day_parts.iterrows():
                self.day_parts_tree.insert(
                    "",
                    "end",
                    values=(
                        day_part,
                        f"${row.get('revenue', 0):,.2f}",
                        int(
                            row.get(
                                "orders",
                                0
                            )
                        ),
                        int(
                            row.get(
                                "items_sold",
                                0
                            )
                        ),
                        f"${row.get('average_order_value', 0):,.2f}",
                        row.get(
                            "most_popular_product",
                            ""
                        )
                    )
                )

    # =========================================================
    # UPDATE PATTERNS
    # =========================================================

    def update_patterns(
        self,
        patterns
    ):
        for row in self.patterns_tree.get_children():
            self.patterns_tree.delete(
                row
            )

        if not patterns:
            self.patterns_tree.insert(
                "",
                "end",
                values=(
                    "None",
                    "",
                    "",
                    "",
                    "No significant patterns detected."
                )
            )

            return

        for pattern in patterns:
            pattern_type = pattern.get(
                "type",
                ""
            )

            item_1 = pattern.get(
                "item_1",
                ""
            )

            item_2 = pattern.get(
                "item_2",
                ""
            )

            strength = pattern.get(
                "strength",
                ""
            )

            description = pattern.get(
                "description",
                ""
            )

            if pattern_type == "Sales relationship":
                try:
                    strength_display = (
                        f"{float(strength):.2f}"
                    )
                except (
                    TypeError,
                    ValueError
                ):
                    strength_display = str(
                        strength
                    )
            else:
                try:
                    strength_display = str(
                        int(strength)
                    )
                except (
                    TypeError,
                    ValueError
                ):
                    strength_display = str(
                        strength
                    )

            self.patterns_tree.insert(
                "",
                "end",
                values=(
                    pattern_type,
                    item_1,
                    item_2,
                    strength_display,
                    description
                )
            )

    # =========================================================
    # UPDATE GRAPHS
    # =========================================================

    def update_graphs(
        self,
        graph_paths
    ):
        self.graphs_listbox.delete(
            0,
            tk.END
        )

        self.graph_paths = []

        for graph in graph_paths:
            path = Path(
                graph
            )

            self.graph_paths.append(
                path
            )

            self.graphs_listbox.insert(
                tk.END,
                path.name
            )

    # =========================================================
    # OPEN GRAPH
    # =========================================================

    def open_selected_graph(self):
        selection = (
            self.graphs_listbox.curselection()
        )

        if not selection:
            messagebox.showwarning(
                "Graphs",
                "Select a graph first."
            )

            return

        index = selection[0]

        if index >= len(
            self.graph_paths
        ):
            return

        graph_path = self.graph_paths[
            index
        ]

        try:
            # macOS
            subprocess.run(
                [
                    "open",
                    str(graph_path)
                ],
                check=False
            )

        except FileNotFoundError:
            try:
                # Linux
                subprocess.run(
                    [
                        "xdg-open",
                        str(graph_path)
                    ],
                    check=False
                )

            except FileNotFoundError:
                try:
                    # Windows
                    os.startfile(
                        str(graph_path)
                    )

                except Exception as error:
                    messagebox.showerror(
                        "Error",
                        f"Could not open graph:\n\n{error}"
                    )


# =============================================================
# MAIN
# =============================================================

def main():
    root = tk.Tk()

    app = BagelyticsApp(
        root
    )

    root.mainloop()


if __name__ == "__main__":
    main()

