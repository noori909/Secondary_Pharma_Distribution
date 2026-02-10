import tkinter as tk
from tkinter import ttk
from logic.area_logic import get_all_areas


class AreasUI(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#ecf0f1")

        tk.Label(
            self,
            text="Areas",
            font=("Arial", 24, "bold"),
            bg="#ecf0f1"
        ).pack(pady=20)

        columns = ("ID", "Name", "Status")

        table = ttk.Treeview(self, columns=columns, show="headings", height=15)
        for col in columns:
            table.heading(col, text=col)
            table.column(col, width=200)

        table.pack(padx=20, pady=10)

        for a in get_all_areas():
            table.insert("", "end", values=(a.id, a.name, a.status))
