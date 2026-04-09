import tkinter as tk
from tkinter import ttk, messagebox
from logic.customer_logic import add_customer, get_all_customers


class CustomersUI(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#ecf0f1")

        tk.Label(
            self,
            text="Customers",
            font=("Arial", 24, "bold"),
            bg="#ecf0f1"
        ).pack(pady=20)

        form = tk.Frame(self, bg="#ecf0f1")
        form.pack(pady=5)

        tk.Label(form, text="Customer Name", bg="#ecf0f1").grid(row=0, column=0, padx=5)
        self.name_entry = tk.Entry(form, width=40)
        self.name_entry.grid(row=0, column=1, padx=5)

        tk.Button(
            form,
            text="Add Customer",
            command=self._add_customer,
            bg="#27ae60",
            fg="white",
            relief="flat",
        ).grid(row=0, column=2, padx=5)

        columns = ("ID", "Name", "Status")
        self.table = ttk.Treeview(self, columns=columns, show="headings", height=15)
        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=220)
        self.table.pack(padx=20, pady=10, fill="x")

        self._load_customers()

    def _load_customers(self):
        for row in self.table.get_children():
            self.table.delete(row)

        for c in get_all_customers():
            self.table.insert("", "end", values=(c.id, c.name, c.status))

    def _add_customer(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Validation Error", "Customer name is required.")
            return

        add_customer(name)
        self.name_entry.delete(0, tk.END)
        self._load_customers()
