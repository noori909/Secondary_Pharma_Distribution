import tkinter as tk
from tkinter import ttk
from logic.sales_logic import get_all_sales


class SalesUI(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#ecf0f1")

        tk.Label(
            self,
            text="Sales",
            font=("Arial", 24, "bold"),
            bg="#ecf0f1"
        ).pack(pady=20)

        columns = (
            "ID", "Date", "Rep ID", "Area ID",
            "Product ID", "Qty", "Net Amount"
        )

        table = ttk.Treeview(self, columns=columns, show="headings", height=15)
        for col in columns:
            table.heading(col, text=col)
            table.column(col, width=120)

        table.pack(padx=20, pady=10, fill="x")

        for s in get_all_sales():
            table.insert(
                "",
                "end",
                values=(
                    s.id, s.date, s.rep_id,
                    s.area_id, s.product_id,
                    s.quantity, s.net_amount
                )
            )
