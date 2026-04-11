import tkinter as tk
from tkinter import ttk, messagebox
from ui.widgets import SearchableCombobox

from logic.product_logic import get_all_products
from logic.stock_logic import get_recent_movements, record_adjustment, record_purchase


class StockUI(tk.Frame):
    REASONS = ("damage", "expiry", "correction", "other")

    def __init__(self, parent):
        super().__init__(parent, bg="#ecf0f1")
        self.product_map = {}

        tk.Label(
            self,
            text="Stock — Purchase & Adjustments",
            font=("Arial", 22, "bold"),
            bg="#ecf0f1",
        ).pack(pady=14)

        sel = tk.LabelFrame(self, text="Product", bg="#ecf0f1")
        sel.pack(fill="x", padx=16, pady=6)
        self.product_combo = SearchableCombobox(sel, width=55)
        self.product_combo.pack(padx=8, pady=8, anchor="w")
        tk.Button(sel, text="Refresh list", command=self._load_products).pack(
            padx=8, pady=(0, 8), anchor="w"
        )

        pur = tk.LabelFrame(self, text="Purchase / inward", bg="#ecf0f1")
        pur.pack(fill="x", padx=16, pady=6)
        tk.Label(pur, text="Quantity", bg="#ecf0f1").grid(row=0, column=0, padx=6, pady=6)
        self.purchase_qty = tk.Entry(pur, width=10)
        self.purchase_qty.grid(row=0, column=1, padx=6, pady=6)
        tk.Label(pur, text="Note (optional)", bg="#ecf0f1").grid(
            row=0, column=2, padx=6, pady=6
        )
        self.purchase_note = tk.Entry(pur, width=40)
        self.purchase_note.grid(row=0, column=3, padx=6, pady=6)
        tk.Button(
            pur,
            text="Add stock",
            command=self._do_purchase,
            bg="#27ae60",
            fg="white",
            relief="flat",
        ).grid(row=0, column=4, padx=10, pady=6)

        adj = tk.LabelFrame(self, text="Adjustment (+/−)", bg="#ecf0f1")
        adj.pack(fill="x", padx=16, pady=6)
        tk.Label(adj, text="Δ Qty (+ add / − remove)", bg="#ecf0f1").grid(
            row=0, column=0, padx=6, pady=6
        )
        self.adj_delta = tk.Entry(adj, width=10)
        self.adj_delta.grid(row=0, column=1, padx=6, pady=6)
        tk.Label(adj, text="Reason", bg="#ecf0f1").grid(row=0, column=2, padx=6, pady=6)
        self.adj_reason = ttk.Combobox(
            adj, values=self.REASONS, state="readonly", width=14
        )
        self.adj_reason.grid(row=0, column=3, padx=6, pady=6)
        self.adj_reason.current(2)
        tk.Label(adj, text="Note (optional)", bg="#ecf0f1").grid(
            row=0, column=4, padx=6, pady=6
        )
        self.adj_note = tk.Entry(adj, width=28)
        self.adj_note.grid(row=0, column=5, padx=6, pady=6)
        tk.Button(
            adj,
            text="Apply adjustment",
            command=self._do_adjustment,
            bg="#2980b9",
            fg="white",
            relief="flat",
        ).grid(row=0, column=6, padx=10, pady=6)

        hist = tk.LabelFrame(self, text="Recent movements (newest first)", bg="#ecf0f1")
        hist.pack(fill="both", expand=True, padx=16, pady=8)
        columns = ("ID", "When", "Product", "Δ", "Reason", "Note", "Stock now")
        self.table = ttk.Treeview(hist, columns=columns, show="headings", height=12)
        widths = (45, 130, 160, 50, 90, 180, 70)
        for col, w in zip(columns, widths):
            self.table.heading(col, text=col)
            self.table.column(col, width=w)
        vs = ttk.Scrollbar(hist, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=vs.set)
        self.table.pack(side="left", fill="both", expand=True)
        vs.pack(side="right", fill="y")

        self._load_products()
        self._refresh_table()

    def _selected_product_id(self):
        label = self.product_combo.get().strip()
        pid = self.product_map.get(label)
        if pid is None:
            messagebox.showerror("Stock", "Select a product.")
            return None
        return pid

    def _load_products(self):
        products = sorted(get_all_products(), key=lambda p: p.name.lower())
        self.product_map = {
            f"{p.id} — {p.name} (stock: {p.quantity_in_stock})": p.id for p in products
        }
        vals = list(self.product_map.keys())
        self.product_combo.set_values(vals)
        if vals:
            self.product_combo.current(0)
        else:
            self.product_combo.set("")

    def _refresh_table(self):
        for iid in self.table.get_children():
            self.table.delete(iid)
        for r in get_recent_movements(150):
            when = r["created_at"]
            if when is not None:
                when = str(when).replace("T", " ")[:19]
            self.table.insert(
                "",
                "end",
                values=(
                    r["id"],
                    when,
                    r["product_name"],
                    f"{r['quantity_delta']:+d}",
                    r["reason"],
                    r["note"][:80] + ("…" if len(r["note"]) > 80 else ""),
                    r["quantity_now"],
                ),
            )

    def _do_purchase(self):
        pid = self._selected_product_id()
        if pid is None:
            return
        try:
            q = int(self.purchase_qty.get().strip())
        except ValueError:
            messagebox.showerror("Stock", "Enter a whole number for quantity.")
            return
        note = self.purchase_note.get().strip() or None
        try:
            record_purchase(pid, q, note=note)
        except ValueError as exc:
            messagebox.showerror("Stock", str(exc))
            return
        self.purchase_qty.delete(0, tk.END)
        self.purchase_note.delete(0, tk.END)
        self._load_products()
        self._refresh_table()
        messagebox.showinfo("Stock", "Purchase recorded.")

    def _do_adjustment(self):
        pid = self._selected_product_id()
        if pid is None:
            return
        try:
            delta = int(self.adj_delta.get().strip())
        except ValueError:
            messagebox.showerror("Stock", "Enter a whole number (e.g. -3 or +2).")
            return
        reason = self.adj_reason.get().strip()
        note = self.adj_note.get().strip() or None
        try:
            record_adjustment(pid, delta, reason, note=note)
        except ValueError as exc:
            messagebox.showerror("Stock", str(exc))
            return
        self.adj_delta.delete(0, tk.END)
        self.adj_note.delete(0, tk.END)
        self._load_products()
        self._refresh_table()
        messagebox.showinfo("Stock", "Adjustment recorded.")
