import tkinter as tk
from tkinter import ttk
from logic.product_logic import get_all_products


class ProductsUI(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#ecf0f1")

        tk.Label(
            self,
            text="Products",
            font=("Arial", 24, "bold"),
            bg="#ecf0f1"
        ).pack(pady=20)

        columns = ("ID", "Name", "Company", "Price", "Status")

        table = ttk.Treeview(self, columns=columns, show="headings", height=15)
        for col in columns:
            table.heading(col, text=col)
            table.column(col, width=150)

        table.pack(padx=20, pady=10, fill="x")

        for p in get_all_products():
            table.insert(
                "",
                "end",
                values=(p.id, p.name, p.company, p.price, p.status)
            )
