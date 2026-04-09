import tkinter as tk
from tkinter import ttk, messagebox
from logic.sales_logic import get_all_sales, record_bill
from logic.rep_logic import get_all_reps
from logic.area_logic import get_all_areas
from logic.customer_logic import get_all_customers
from logic.product_logic import get_all_products


class SalesUI(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#ecf0f1")
        self.bill_items = []
        self.rep_map = {}
        self.area_map = {}
        self.customer_map = {}
        self.product_map = {}

        tk.Label(
            self,
            text="Sales / Billing",
            font=("Arial", 24, "bold"),
            bg="#ecf0f1"
        ).pack(pady=20)

        self._build_bill_header()
        self._build_item_entry()
        self._build_bill_table()
        self._build_actions()
        self._build_sales_history()
        self._refresh_dropdowns()
        self._refresh_sales_history()

    def _build_bill_header(self):
        header = tk.Frame(self, bg="#ecf0f1")
        header.pack(padx=20, pady=5, fill="x")

        tk.Label(header, text="Rep", bg="#ecf0f1").grid(row=0, column=0, padx=5, sticky="w")
        self.rep_combo = ttk.Combobox(header, width=28, state="readonly")
        self.rep_combo.grid(row=0, column=1, padx=5)

        tk.Label(header, text="Area", bg="#ecf0f1").grid(row=0, column=2, padx=5, sticky="w")
        self.area_combo = ttk.Combobox(header, width=28, state="readonly")
        self.area_combo.grid(row=0, column=3, padx=5)

        tk.Label(header, text="Customer (optional)", bg="#ecf0f1").grid(row=0, column=4, padx=5, sticky="w")
        self.customer_combo = ttk.Combobox(header, width=30, state="readonly")
        self.customer_combo.grid(row=0, column=5, padx=5)

    def _build_item_entry(self):
        item_box = tk.LabelFrame(self, text="Add Bill Item", bg="#ecf0f1")
        item_box.pack(padx=20, pady=8, fill="x")

        tk.Label(item_box, text="Product", bg="#ecf0f1").grid(row=0, column=0, padx=5, pady=8)
        self.product_combo = ttk.Combobox(item_box, width=40, state="readonly")
        self.product_combo.grid(row=0, column=1, padx=5)

        tk.Label(item_box, text="Qty", bg="#ecf0f1").grid(row=0, column=2, padx=5)
        self.qty_entry = tk.Entry(item_box, width=8)
        self.qty_entry.grid(row=0, column=3, padx=5)

        tk.Label(item_box, text="Discount", bg="#ecf0f1").grid(row=0, column=4, padx=5)
        self.discount_entry = tk.Entry(item_box, width=10)
        self.discount_entry.insert(0, "0")
        self.discount_entry.grid(row=0, column=5, padx=5)

        tk.Button(
            item_box,
            text="Add Line",
            command=self._add_line_item,
            bg="#2980b9",
            fg="white",
            relief="flat",
        ).grid(row=0, column=6, padx=10)

    def _build_bill_table(self):
        columns = ("Product", "TP", "MRP", "Qty", "Discount", "Line Total")
        self.bill_table = ttk.Treeview(self, columns=columns, show="headings", height=8)
        for col in columns:
            self.bill_table.heading(col, text=col)
            self.bill_table.column(col, width=140)
        self.bill_table.pack(padx=20, pady=8, fill="x")

        self.total_label = tk.Label(
            self,
            text="Bill Total: 0.00",
            font=("Arial", 13, "bold"),
            bg="#ecf0f1",
        )
        self.total_label.pack(padx=20, anchor="e")

    def _build_actions(self):
        actions = tk.Frame(self, bg="#ecf0f1")
        actions.pack(padx=20, pady=8, fill="x")

        tk.Button(
            actions,
            text="Remove Selected Line",
            command=self._remove_selected_line,
            bg="#c0392b",
            fg="white",
            relief="flat",
        ).pack(side="left", padx=5)

        tk.Button(
            actions,
            text="Clear Bill",
            command=self._clear_bill,
            bg="#7f8c8d",
            fg="white",
            relief="flat",
        ).pack(side="left", padx=5)

        tk.Button(
            actions,
            text="Save Bill",
            command=self._save_bill,
            bg="#27ae60",
            fg="white",
            relief="flat",
        ).pack(side="right", padx=5)

    def _build_sales_history(self):
        tk.Label(
            self,
            text="Recent Sales",
            font=("Arial", 14, "bold"),
            bg="#ecf0f1",
        ).pack(anchor="w", padx=20, pady=(8, 2))

        columns = ("ID", "Date", "Rep", "Area", "Customer", "Qty", "Net")
        self.sales_table = ttk.Treeview(self, columns=columns, show="headings", height=8)
        for col in columns:
            self.sales_table.heading(col, text=col)
            self.sales_table.column(col, width=110)
        self.sales_table.pack(padx=20, pady=4, fill="x")

    def _refresh_dropdowns(self):
        reps = get_all_reps(include_inactive=False)
        self.rep_map = {f"{r.id} - {r.name}": r.id for r in reps}
        self.rep_combo["values"] = list(self.rep_map.keys())
        if reps:
            self.rep_combo.current(0)

        areas = get_all_areas(include_inactive=False)
        self.area_map = {f"{a.id} - {a.name}": a.id for a in areas}
        self.area_combo["values"] = list(self.area_map.keys())
        if areas:
            self.area_combo.current(0)

        customers = get_all_customers(include_inactive=False)
        customer_values = ["(None)"]
        self.customer_map = {"(None)": None}
        for c in customers:
            label = f"{c.id} - {c.name}"
            customer_values.append(label)
            self.customer_map[label] = c.id
        self.customer_combo["values"] = customer_values
        self.customer_combo.current(0)

        products = [p for p in get_all_products() if p.status == "active" and p.quantity_in_stock > 0]
        self.product_map = {
            f"{p.id} - {p.name} (Stock: {p.quantity_in_stock})": p for p in products
        }
        self.product_combo["values"] = list(self.product_map.keys())
        if products:
            self.product_combo.current(0)

    def _refresh_sales_history(self):
        for row in self.sales_table.get_children():
            self.sales_table.delete(row)

        for s in get_all_sales()[-25:]:
            customer_value = s.customer_id if s.customer_id is not None else "-"
            self.sales_table.insert(
                "",
                "end",
                values=(s.id, s.date, s.rep_id, s.area_id, customer_value, s.quantity, f"{s.net_amount:.2f}"),
            )

    def _add_line_item(self):
        product_label = self.product_combo.get().strip()
        if not product_label:
            messagebox.showerror("Validation Error", "Select a product.")
            return

        try:
            quantity = int(self.qty_entry.get().strip())
            discount = float(self.discount_entry.get().strip() or "0")
        except ValueError:
            messagebox.showerror("Validation Error", "Quantity must be integer and discount must be number.")
            return

        if quantity <= 0:
            messagebox.showerror("Validation Error", "Quantity must be positive.")
            return
        if discount < 0:
            messagebox.showerror("Validation Error", "Discount cannot be negative.")
            return

        product = self.product_map.get(product_label)
        if not product:
            messagebox.showerror("Validation Error", "Invalid product selected.")
            return

        line_total = (product.trade_price * quantity) - discount
        if line_total <= 0:
            messagebox.showerror("Validation Error", "Discount is too high for this line.")
            return

        item = {
            "product_id": product.id,
            "product_name": product.name,
            "trade_price": product.trade_price,
            "mrp": product.mrp,
            "quantity": quantity,
            "discount": discount,
            "line_total": line_total,
        }
        self.bill_items.append(item)
        self._render_bill_table()

        self.qty_entry.delete(0, tk.END)
        self.discount_entry.delete(0, tk.END)
        self.discount_entry.insert(0, "0")

    def _render_bill_table(self):
        for row in self.bill_table.get_children():
            self.bill_table.delete(row)

        total = 0.0
        for idx, item in enumerate(self.bill_items):
            total += item["line_total"]
            self.bill_table.insert(
                "",
                "end",
                iid=str(idx),
                values=(
                    item["product_name"],
                    f"{item['trade_price']:.2f}",
                    f"{item['mrp']:.2f}",
                    item["quantity"],
                    f"{item['discount']:.2f}",
                    f"{item['line_total']:.2f}",
                ),
            )

        self.total_label.config(text=f"Bill Total: {total:.2f}")

    def _remove_selected_line(self):
        selected = self.bill_table.selection()
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(self.bill_items):
            self.bill_items.pop(idx)
            self._render_bill_table()

    def _clear_bill(self):
        self.bill_items = []
        self._render_bill_table()

    def _save_bill(self):
        if not self.bill_items:
            messagebox.showerror("Validation Error", "Add at least one line item.")
            return

        rep_label = self.rep_combo.get().strip()
        area_label = self.area_combo.get().strip()
        customer_label = self.customer_combo.get().strip() or "(None)"

        rep_id = self.rep_map.get(rep_label)
        area_id = self.area_map.get(area_label)
        customer_id = self.customer_map.get(customer_label)

        if not rep_id:
            messagebox.showerror("Validation Error", "Select a rep.")
            return
        if not area_id:
            messagebox.showerror("Validation Error", "Select an area.")
            return

        payload_items = [
            {
                "product_id": item["product_id"],
                "quantity": item["quantity"],
                "discount": item["discount"],
            }
            for item in self.bill_items
        ]

        try:
            sale_id = record_bill(
                rep_id=rep_id,
                area_id=area_id,
                customer_id=customer_id,
                items=payload_items,
            )
        except ValueError as exc:
            messagebox.showerror("Save Failed", str(exc))
            return

        messagebox.showinfo("Saved", f"Bill saved successfully. Sale ID: {sale_id}")
        self._clear_bill()
        self._refresh_dropdowns()
        self._refresh_sales_history()
