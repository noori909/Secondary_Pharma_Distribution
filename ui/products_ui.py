import tkinter as tk
from tkinter import ttk, messagebox

from logic.product_logic import (
    add_product,
    get_all_products,
    set_product_status,
    update_product,
)


class ProductsUI(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#ecf0f1")
        self._editing_id = None

        tk.Label(
            self,
            text="Products",
            font=("Arial", 24, "bold"),
            bg="#ecf0f1",
        ).pack(pady=12)

        self.mode_label = tk.Label(
            self,
            text="New product",
            font=("Arial", 11, "italic"),
            bg="#ecf0f1",
        )
        self.mode_label.pack()

        form = tk.LabelFrame(self, text="Details", bg="#ecf0f1")
        form.pack(fill="x", padx=16, pady=8)

        r = 0
        tk.Label(form, text="Name *", bg="#ecf0f1").grid(row=r, column=0, sticky="e", padx=6, pady=3)
        self.name_e = tk.Entry(form, width=36)
        self.name_e.grid(row=r, column=1, columnspan=3, sticky="we", padx=6, pady=3)
        r += 1

        tk.Label(form, text="Company *", bg="#ecf0f1").grid(row=r, column=0, sticky="e", padx=6, pady=3)
        self.company_e = tk.Entry(form, width=36)
        self.company_e.grid(row=r, column=1, columnspan=3, sticky="we", padx=6, pady=3)
        r += 1

        tk.Label(form, text="Trade price (TP) *", bg="#ecf0f1").grid(
            row=r, column=0, sticky="e", padx=6, pady=3
        )
        self.tp_e = tk.Entry(form, width=12)
        self.tp_e.grid(row=r, column=1, sticky="w", padx=6, pady=3)
        tk.Label(form, text="MRP *", bg="#ecf0f1").grid(row=r, column=2, sticky="e", padx=6, pady=3)
        self.mrp_e = tk.Entry(form, width=12)
        self.mrp_e.grid(row=r, column=3, sticky="w", padx=6, pady=3)
        r += 1

        tk.Label(form, text="Batch", bg="#ecf0f1").grid(row=r, column=0, sticky="e", padx=6, pady=3)
        self.batch_e = tk.Entry(form, width=20)
        self.batch_e.grid(row=r, column=1, sticky="w", padx=6, pady=3)
        tk.Label(form, text="Formula", bg="#ecf0f1").grid(row=r, column=2, sticky="e", padx=6, pady=3)
        self.formula_e = tk.Entry(form, width=20)
        self.formula_e.grid(row=r, column=3, sticky="w", padx=6, pady=3)
        r += 1

        tk.Label(form, text="Description", bg="#ecf0f1").grid(
            row=r, column=0, sticky="ne", padx=6, pady=3
        )
        self.desc_t = tk.Text(form, width=50, height=3, wrap="word")
        self.desc_t.grid(row=r, column=1, columnspan=3, sticky="we", padx=6, pady=3)
        r += 1

        tk.Label(form, text="Initial stock", bg="#ecf0f1").grid(
            row=r, column=0, sticky="e", padx=6, pady=3
        )
        self.stock_row_frame = tk.Frame(form, bg="#ecf0f1")
        self.stock_row_frame.grid(row=r, column=1, columnspan=3, sticky="w", padx=6, pady=3)
        self.stock_e = tk.Entry(self.stock_row_frame, width=10)
        self.stock_e.pack(side="left")
        self.stock_e.insert(0, "0")
        tk.Label(
            self.stock_row_frame,
            text="(new only — use Stock screen to change later)",
            bg="#ecf0f1",
            fg="#555",
            font=("Arial", 8),
        ).pack(side="left", padx=8)
        self.stock_readonly_lbl = tk.Label(self.stock_row_frame, bg="#ecf0f1", font=("Arial", 10, "bold"))

        btn_row = tk.Frame(self, bg="#ecf0f1")
        btn_row.pack(pady=8)
        tk.Button(
            btn_row,
            text="Add product",
            command=self._add_product,
            bg="#27ae60",
            fg="white",
            relief="flat",
            width=14,
        ).pack(side="left", padx=4)
        tk.Button(
            btn_row,
            text="Save changes",
            command=self._save_changes,
            bg="#2980b9",
            fg="white",
            relief="flat",
            width=14,
        ).pack(side="left", padx=4)
        tk.Button(
            btn_row,
            text="Clear / new",
            command=self._clear_form,
            bg="#7f8c8d",
            fg="white",
            relief="flat",
            width=14,
        ).pack(side="left", padx=4)
        tk.Button(
            btn_row,
            text="Load selected",
            command=self._load_selected,
            bg="#34495e",
            fg="white",
            relief="flat",
            width=14,
        ).pack(side="left", padx=4)

        btn_row2 = tk.Frame(self, bg="#ecf0f1")
        btn_row2.pack(pady=4)
        tk.Button(
            btn_row2,
            text="Deactivate selected",
            command=lambda: self._set_status_selected("inactive"),
            bg="#c0392b",
            fg="white",
            relief="flat",
            width=18,
        ).pack(side="left", padx=4)
        tk.Button(
            btn_row2,
            text="Activate selected",
            command=lambda: self._set_status_selected("active"),
            bg="#16a085",
            fg="white",
            relief="flat",
            width=18,
        ).pack(side="left", padx=4)

        list_frame = tk.LabelFrame(self, text="All products", bg="#ecf0f1")
        list_frame.pack(fill="both", expand=True, padx=16, pady=8)

        columns = ("ID", "Name", "Company", "TP", "MRP", "Stock", "Batch", "Status")
        self.table = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        widths = (40, 140, 100, 55, 55, 50, 80, 70)
        for col, w in zip(columns, widths):
            self.table.heading(col, text=col)
            self.table.column(col, width=w)
        vs = ttk.Scrollbar(list_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=vs.set)
        self.table.pack(side="left", fill="both", expand=True)
        vs.pack(side="right", fill="y")
        self.table.bind("<Double-1>", lambda _e: self._load_selected())

        self._clear_form()
        self._refresh_table()

    def _clear_form(self):
        self._editing_id = None
        self.mode_label.config(text="New product")
        for w in (
            self.name_e,
            self.company_e,
            self.tp_e,
            self.mrp_e,
            self.batch_e,
            self.formula_e,
        ):
            w.delete(0, tk.END)
        self.desc_t.delete("1.0", tk.END)
        self.stock_e.config(state="normal")
        self.stock_e.delete(0, tk.END)
        self.stock_e.insert(0, "0")
        self.stock_readonly_lbl.config(text="")
        self.stock_readonly_lbl.pack_forget()

    def _parse_float(self, raw, label):
        try:
            return float(str(raw).strip())
        except ValueError:
            raise ValueError(f"{label} must be a number")

    def _get_form_payload(self, include_initial_stock):
        name = self.name_e.get().strip()
        company = self.company_e.get().strip()
        if not name or not company:
            raise ValueError("Name and company are required.")

        tp = self._parse_float(self.tp_e.get(), "Trade price")
        mrp_raw = self.mrp_e.get().strip()
        mrp = self._parse_float(mrp_raw, "MRP") if mrp_raw else tp

        batch = self.batch_e.get().strip() or None
        formula = self.formula_e.get().strip() or None
        desc = self.desc_t.get("1.0", tk.END).strip() or None

        qty = 0
        if include_initial_stock:
            try:
                qty = int(self.stock_e.get().strip() or "0")
            except ValueError:
                raise ValueError("Initial stock must be a whole number")
            if qty < 0:
                raise ValueError("Initial stock cannot be negative")

        return name, company, tp, mrp, batch, formula, desc, qty

    def _add_product(self):
        try:
            name, company, tp, mrp, batch, formula, desc, qty = self._get_form_payload(
                include_initial_stock=True
            )
        except ValueError as exc:
            messagebox.showerror("Products", str(exc))
            return
        try:
            add_product(
                name,
                company,
                tp,
                mrp=mrp,
                quantity=qty,
                batch=batch,
                formula=formula,
                description=desc,
            )
        except Exception as exc:
            messagebox.showerror("Products", str(exc))
            return
        self._clear_form()
        self._refresh_table()
        messagebox.showinfo("Products", "Product added.")

    def _save_changes(self):
        if self._editing_id is None:
            messagebox.showinfo("Products", "Load a product first, or use Add product.")
            return
        try:
            name, company, tp, mrp, batch, formula, desc, _ = self._get_form_payload(
                include_initial_stock=False
            )
        except ValueError as exc:
            messagebox.showerror("Products", str(exc))
            return
        try:
            update_product(
                self._editing_id,
                name,
                company,
                tp,
                mrp,
                batch=batch,
                formula=formula,
                description=desc,
            )
        except ValueError as exc:
            messagebox.showerror("Products", str(exc))
            return
        self._refresh_table()
        messagebox.showinfo("Products", "Saved.")

    def _load_selected(self):
        sel = self.table.selection()
        if not sel:
            messagebox.showinfo("Products", "Select a row in the table.")
            return
        vals = self.table.item(sel[0], "values")
        if not vals:
            return
        try:
            pid = int(vals[0])
        except ValueError:
            return

        products = {p.id: p for p in get_all_products()}
        p = products.get(pid)
        if not p:
            self._refresh_table()
            return

        self._editing_id = pid
        self.mode_label.config(text=f"Editing product #{pid}")
        self.name_e.delete(0, tk.END)
        self.name_e.insert(0, p.name)
        self.company_e.delete(0, tk.END)
        self.company_e.insert(0, p.company)
        self.tp_e.delete(0, tk.END)
        self.tp_e.insert(0, str(p.trade_price))
        self.mrp_e.delete(0, tk.END)
        self.mrp_e.insert(0, str(p.mrp))
        self.batch_e.delete(0, tk.END)
        if p.batch:
            self.batch_e.insert(0, p.batch)
        self.formula_e.delete(0, tk.END)
        if p.formula:
            self.formula_e.insert(0, p.formula)
        self.desc_t.delete("1.0", tk.END)
        if p.description:
            self.desc_t.insert("1.0", p.description)

        self.stock_e.config(state="disabled")
        self.stock_readonly_lbl.config(
            text=f"Current stock: {p.quantity_in_stock} (change under Stock)"
        )
        self.stock_readonly_lbl.pack(side="left", padx=8)

    def _set_status_selected(self, status):
        sel = self.table.selection()
        if not sel:
            messagebox.showinfo("Products", "Select a row in the table.")
            return
        vals = self.table.item(sel[0], "values")
        try:
            pid = int(vals[0])
        except (ValueError, IndexError):
            return
        try:
            set_product_status(pid, status)
        except ValueError as exc:
            messagebox.showerror("Products", str(exc))
            return
        self._refresh_table()
        if self._editing_id == pid:
            self._clear_form()

    def _refresh_table(self):
        for iid in self.table.get_children():
            self.table.delete(iid)
        for p in sorted(get_all_products(), key=lambda x: x.name.lower()):
            batch = (p.batch or "")[:12]
            self.table.insert(
                "",
                "end",
                values=(
                    p.id,
                    p.name,
                    p.company,
                    f"{p.trade_price:.2f}",
                    f"{p.mrp:.2f}",
                    p.quantity_in_stock,
                    batch,
                    p.status,
                ),
            )
