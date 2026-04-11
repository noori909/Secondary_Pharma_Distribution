import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from ui.widgets import SearchableCombobox

from logic.area_logic import get_all_areas
from logic.customer_logic import get_all_customers
from logic.product_logic import get_all_products
from logic.rep_logic import get_all_reps
from logic.report_logic import (
    get_report_detail_rows,
    summarize_totals,
    aggregate_by_rep,
    aggregate_by_area,
    aggregate_by_product,
    aggregate_by_customer,
    get_stock_movement_report_rows,
    summarize_stock_movements,
)


class ReportsUI(tk.Frame):
    MODES = (
        ("detail", "Detail (line items)"),
        ("rep", "Summary by rep"),
        ("area", "Summary by area"),
        ("product", "Summary by product"),
        ("customer", "Summary by customer"),
        ("stock", "Stock movements"),
    )

    def __init__(self, parent):
        super().__init__(parent, bg="#ecf0f1")
        self._detail_rows = []
        self._stock_rows = []
        self.rep_map = {}
        self.area_map = {}
        self.product_map = {}
        self.customer_map = {}
        self.reason_map = {}

        tk.Label(
            self,
            text="Reports",
            font=("Arial", 24, "bold"),
            bg="#ecf0f1",
        ).pack(pady=12)

        self._build_filters()
        self._build_summary()
        self._build_stock_summary()
        self._build_export()
        self._build_mode_and_table()
        self._load_filter_options()
        self._run_report()

    def _build_filters(self):
        box = tk.LabelFrame(self, text="Filters", bg="#ecf0f1")
        box.pack(fill="x", padx=16, pady=6)

        tk.Label(box, text="From (YYYY-MM-DD)", bg="#ecf0f1").grid(
            row=0, column=0, padx=4, pady=4, sticky="w"
        )
        self.date_from = tk.Entry(box, width=14)
        self.date_from.grid(row=0, column=1, padx=4, pady=4)

        tk.Label(box, text="To (YYYY-MM-DD)", bg="#ecf0f1").grid(
            row=0, column=2, padx=4, pady=4, sticky="w"
        )
        self.date_to = tk.Entry(box, width=14)
        self.date_to.grid(row=0, column=3, padx=4, pady=4)

        tk.Label(box, text="Rep", bg="#ecf0f1").grid(
            row=1, column=0, padx=4, pady=4, sticky="w"
        )
        self.rep_combo = SearchableCombobox(box, width=22)
        self.rep_combo.grid(row=1, column=1, padx=4, pady=4)

        tk.Label(box, text="Area", bg="#ecf0f1").grid(
            row=1, column=2, padx=4, pady=4, sticky="w"
        )
        self.area_combo = SearchableCombobox(box, width=22)
        self.area_combo.grid(row=1, column=3, padx=4, pady=4)

        tk.Label(box, text="Product", bg="#ecf0f1").grid(
            row=2, column=0, padx=4, pady=4, sticky="w"
        )
        self.product_combo = SearchableCombobox(box, width=36)
        self.product_combo.grid(row=2, column=1, columnspan=2, padx=4, pady=4, sticky="we")

        tk.Label(box, text="Customer", bg="#ecf0f1").grid(
            row=2, column=3, padx=4, pady=4, sticky="w"
        )
        self.customer_combo = SearchableCombobox(box, width=24)
        self.customer_combo.grid(row=2, column=4, padx=4, pady=4)

        tk.Label(box, text="Stock reason", bg="#ecf0f1").grid(
            row=3, column=0, padx=4, pady=4, sticky="w"
        )
        self.reason_combo = ttk.Combobox(box, width=22, state="readonly")
        self.reason_combo.grid(row=3, column=1, padx=4, pady=4, sticky="w")

        tk.Button(
            box,
            text="Run report",
            command=self._run_report,
            bg="#2980b9",
            fg="white",
            relief="flat",
            width=20
        ).grid(row=3, column=3, columnspan=2, padx=12, pady=4, sticky="e")

    def _build_summary(self):
        self.summary_frame = tk.LabelFrame(self, text="Totals (filtered)", bg="#ecf0f1")
        self.summary_frame.pack(fill="x", padx=16, pady=4)
        self.summary_labels = {}
        keys = [
            ("bills", "Bills"),
            ("lines", "Lines"),
            ("qty", "Qty"),
            ("disc", "Line discounts"),
            ("net", "Net sales"),
            ("ben", "Est. benefit (8%)"),
        ]
        for i, (key, title) in enumerate(keys):
            tk.Label(self.summary_frame, text=f"{title}:", bg="#ecf0f1").grid(
                row=0, column=i * 2, padx=6, pady=4, sticky="e"
            )
            lbl = tk.Label(
                self.summary_frame,
                text="—",
                font=("Arial", 10, "bold"),
                bg="#ecf0f1",
            )
            lbl.grid(row=0, column=i * 2 + 1, padx=6, pady=4, sticky="w")
            self.summary_labels[key] = lbl

    def _build_stock_summary(self):
        self.stock_summary_frame = tk.LabelFrame(
            self, text="Stock movements (same dates & product; reason filter)", bg="#ecf0f1"
        )
        self.stock_summary_frame.pack(fill="x", padx=16, pady=4)
        self.stock_summary_labels = {}
        keys = [
            ("mov", "Movements"),
            ("in", "Qty in (+)"),
            ("out", "Qty out (-)"),
            ("net", "Net Δ"),
        ]
        for i, (key, title) in enumerate(keys):
            tk.Label(self.stock_summary_frame, text=f"{title}:", bg="#ecf0f1").grid(
                row=0, column=i * 2, padx=6, pady=4, sticky="e"
            )
            lbl = tk.Label(
                self.stock_summary_frame,
                text="—",
                font=("Arial", 10, "bold"),
                bg="#ecf0f1",
            )
            lbl.grid(row=0, column=i * 2 + 1, padx=6, pady=4, sticky="w")
            self.stock_summary_labels[key] = lbl

    def _build_mode_and_table(self):
        bar = tk.Frame(self, bg="#ecf0f1")
        bar.pack(fill="x", padx=16, pady=4)

        tk.Label(bar, text="View", bg="#ecf0f1").pack(side="left", padx=(0, 6))
        self.mode_combo = ttk.Combobox(
            bar,
            state="readonly",
            width=28,
            values=[label for _k, label in self.MODES],
        )
        self.mode_combo.pack(side="left")
        self.mode_combo.current(0)
        self.mode_combo.bind("<<ComboboxSelected>>", lambda _e: self._render_table())

        self.table_frame = tk.Frame(self, bg="#ecf0f1")
        self.table_frame.pack(fill="both", expand=True, padx=16, pady=6)

        self.tree = None
        self.vscroll = None
        self.hscroll = None

    def _ensure_tree(self, columns, headings, widths):
        if self.tree is not None:
            self.tree.destroy()
        if self.vscroll is not None:
            self.vscroll.destroy()
        if self.hscroll is not None:
            self.hscroll.destroy()

        self.vscroll = ttk.Scrollbar(self.table_frame, orient="vertical")
        self.hscroll = ttk.Scrollbar(self.table_frame, orient="horizontal")

        self.tree = ttk.Treeview(
            self.table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=self.vscroll.set,
            xscrollcommand=self.hscroll.set,
            height=14,
        )
        self.vscroll.config(command=self.tree.yview)
        self.hscroll.config(command=self.tree.xview)

        for col, h, w in zip(columns, headings, widths):
            self.tree.heading(col, text=h)
            self.tree.column(col, width=w, minwidth=40)

        self.tree.grid(row=0, column=0, sticky="nsew")
        self.vscroll.grid(row=0, column=1, sticky="ns")
        self.hscroll.grid(row=1, column=0, sticky="ew")
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

    def _build_export(self):
        row = tk.Frame(self, bg="#ecf0f1")
        row.pack(side="bottom", fill="x", padx=16, pady=8)
        tk.Button(
            row,
            text="Export current view to CSV…",
            command=self._export_csv,
            bg="#16a085",
            fg="white",
            relief="flat",
            width=26
        ).pack(side="left")
        
        tk.Button(
            row,
            text="Export current view to PDF…",
            command=self._export_pdf,
            bg="#8e44ad",
            fg="white",
            relief="flat",
            width=26
        ).pack(side="left", padx=10)

    def _load_filter_options(self):
        reps = get_all_reps(include_inactive=False)
        self.rep_map = {"(All)": None}
        rep_vals = ["(All)"]
        for r in reps:
            label = f"{r.id} — {r.name}"
            rep_vals.append(label)
            self.rep_map[label] = r.id
        self.rep_combo.set_values(rep_vals)
        self.rep_combo.current(0)

        areas = get_all_areas(include_inactive=False)
        self.area_map = {"(All)": None}
        area_vals = ["(All)"]
        for a in areas:
            label = f"{a.id} — {a.name}"
            area_vals.append(label)
            self.area_map[label] = a.id
        self.area_combo.set_values(area_vals)
        self.area_combo.current(0)

        products = get_all_products()
        self.product_map = {"(All)": None}
        prod_vals = ["(All)"]
        for p in products:
            label = f"{p.id} — {p.name}"
            prod_vals.append(label)
            self.product_map[label] = p.id
        self.product_combo.set_values(prod_vals)
        self.product_combo.current(0)

        customers = get_all_customers(include_inactive=False)
        self.customer_map = {"(All)": None}
        cust_vals = ["(All)"]
        for c in customers:
            label = f"{c.id} — {c.name}"
            cust_vals.append(label)
            self.customer_map[label] = c.id
        self.customer_combo.set_values(cust_vals)
        self.customer_combo.current(0)

        self.reason_map = {
            "(All)": None,
            "purchase": "purchase",
            "damage": "damage",
            "expiry": "expiry",
            "correction": "correction",
            "other": "other",
        }
        self.reason_combo["values"] = list(self.reason_map.keys())
        self.reason_combo.current(0)

    def _selected_id(self, combo, mapping):
        label = combo.get().strip()
        return mapping.get(label)

    def _run_report(self):
        df = self.date_from.get().strip() or None
        dt = self.date_to.get().strip() or None
        try:
            self._detail_rows = get_report_detail_rows(
                date_from=df,
                date_to=dt,
                rep_id=self._selected_id(self.rep_combo, self.rep_map),
                area_id=self._selected_id(self.area_combo, self.area_map),
                product_id=self._selected_id(self.product_combo, self.product_map),
                customer_id=self._selected_id(self.customer_combo, self.customer_map),
            )
        except ValueError as exc:
            messagebox.showerror("Report", str(exc))
            return

        t = summarize_totals(self._detail_rows)
        self.summary_labels["bills"].config(text=str(t["bill_count"]))
        self.summary_labels["lines"].config(text=str(t["line_count"]))
        self.summary_labels["qty"].config(text=str(t["quantity"]))
        self.summary_labels["disc"].config(text=f"{t['line_discount']:.2f}")
        self.summary_labels["net"].config(text=f"{t['net_sales']:.2f}")
        self.summary_labels["ben"].config(text=f"{t['benefit_8pct']:.2f}")

        try:
            self._stock_rows = get_stock_movement_report_rows(
                date_from=df,
                date_to=dt,
                product_id=self._selected_id(self.product_combo, self.product_map),
                reason=self._selected_id(self.reason_combo, self.reason_map),
            )
        except ValueError as exc:
            messagebox.showerror("Report", str(exc))
            return

        st = summarize_stock_movements(self._stock_rows)
        self.stock_summary_labels["mov"].config(text=str(st["movement_count"]))
        self.stock_summary_labels["in"].config(text=str(st["qty_in"]))
        self.stock_summary_labels["out"].config(text=str(st["qty_out"]))
        self.stock_summary_labels["net"].config(text=str(st["net_delta"]))

        self._render_table()

    def _current_mode_key(self):
        label = self.mode_combo.get()
        for key, lab in self.MODES:
            if lab == label:
                return key
        return "detail"

    def _render_table(self):
        mode = self._current_mode_key()

        if mode == "detail":
            cols = (
                "sale_id",
                "sale_date",
                "rep_name",
                "area_name",
                "customer_name",
                "product_name",
                "company",
                "batch",
                "qty",
                "line_disc",
                "line_net",
                "bill_net",
            )
            heads = (
                "Bill",
                "Date",
                "Rep",
                "Area",
                "Customer",
                "Product",
                "Company",
                "Batch",
                "Qty",
                "Disc",
                "Line net",
                "Bill net",
            )
            widths = (50, 85, 90, 90, 100, 120, 80, 70, 45, 55, 75, 75)
            self._ensure_tree(cols, heads, widths)
            for r in self._detail_rows:
                base = r["trade_price"] * r["quantity"]
                pct = (r["line_discount"] / base * 100) if base > 0 else 0
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        r["sale_id"],
                        r["sale_date"],
                        r["rep_name"],
                        r["area_name"],
                        r["customer_name"],
                        r["product_name"],
                        r["company"],
                        r["batch"],
                        r["quantity"],
                        f"{pct:.2f}%",
                        f"{r['line_net']:.2f}",
                        f"{r['sale_net_amount']:.2f}",
                    ),
                )
            return

        if mode == "rep":
            rows = aggregate_by_rep(self._detail_rows)
            cols = ("rep_name", "bills", "qty", "disc", "net", "ben")
            heads = ("Rep", "Bills", "Qty", "Line disc", "Net sales", "8% benefit")
            widths = (140, 55, 55, 80, 90, 90)
            self._ensure_tree(cols, heads, widths)
            for r in rows:
                base = r['net_sales'] + r['line_discount']
                pct = (r['line_discount'] / base * 100) if base > 0 else 0
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        r["rep_name"],
                        r["bills"],
                        r["quantity"],
                        f"{pct:.2f}%",
                        f"{r['net_sales']:.2f}",
                        f"{r['benefit_8pct']:.2f}",
                    ),
                )
            return

        if mode == "area":
            rows = aggregate_by_area(self._detail_rows)
            cols = ("area_name", "bills", "qty", "disc", "net", "ben")
            heads = ("Area", "Bills", "Qty", "Line disc", "Net sales", "8% benefit")
            widths = (140, 55, 55, 80, 90, 90)
            self._ensure_tree(cols, heads, widths)
            for r in rows:
                base = r['net_sales'] + r['line_discount']
                pct = (r['line_discount'] / base * 100) if base > 0 else 0
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        r["area_name"],
                        r["bills"],
                        r["quantity"],
                        f"{pct:.2f}%",
                        f"{r['net_sales']:.2f}",
                        f"{r['benefit_8pct']:.2f}",
                    ),
                )
            return

        if mode == "product":
            rows = aggregate_by_product(self._detail_rows)
            cols = ("product_name", "company", "bills", "qty", "disc", "net", "ben")
            heads = (
                "Product",
                "Company",
                "Bills",
                "Qty",
                "Line disc",
                "Net sales",
                "8% benefit",
            )
            widths = (160, 90, 55, 55, 75, 85, 85)
            self._ensure_tree(cols, heads, widths)
            for r in rows:
                base = r['net_sales'] + r['line_discount']
                pct = (r['line_discount'] / base * 100) if base > 0 else 0
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        r["product_name"],
                        r["company"],
                        r["bills"],
                        r["quantity"],
                        f"{pct:.2f}%",
                        f"{r['net_sales']:.2f}",
                        f"{r['benefit_8pct']:.2f}",
                    ),
                )
            return

        if mode == "customer":
            rows = aggregate_by_customer(self._detail_rows)
            cols = ("customer_name", "bills", "qty", "disc", "net", "ben")
            heads = ("Customer", "Bills", "Qty", "Line disc", "Net sales", "8% benefit")
            widths = (160, 55, 55, 80, 90, 90)
            self._ensure_tree(cols, heads, widths)
            for r in rows:
                base = r['net_sales'] + r['line_discount']
                pct = (r['line_discount'] / base * 100) if base > 0 else 0
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        r["customer_name"],
                        r["bills"],
                        r["quantity"],
                        f"{pct:.2f}%",
                        f"{r['net_sales']:.2f}",
                        f"{r['benefit_8pct']:.2f}",
                    ),
                )
            return

        if mode == "stock":
            cols = ("id", "when", "product", "company", "delta", "reason", "note")
            heads = ("ID", "When", "Product", "Company", "Δ", "Reason", "Note")
            widths = (45, 130, 160, 90, 50, 90, 200)
            self._ensure_tree(cols, heads, widths)
            for r in self._stock_rows:
                when = r["created_at"]
                if when is not None:
                    when = str(when).replace("T", " ")[:19]
                note = r["note"] or ""
                if len(note) > 80:
                    note = note[:80] + "…"
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        r["movement_id"],
                        when,
                        r["product_name"],
                        r["company"],
                        f"{r['quantity_delta']:+d}",
                        r["reason"],
                        note,
                    ),
                )
            return

    def _export_csv(self):
        mode = self._current_mode_key()
        if mode != "stock" and not self._detail_rows:
            messagebox.showinfo("Export", "Run a report first.")
            return

        path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("All", "*.*")],
            initialfile=f"report_{mode}.csv",
        )
        if not path:
            return

        try:
            if mode == "stock":
                fieldnames = [
                    "movement_id",
                    "created_at",
                    "product_id",
                    "product_name",
                    "company",
                    "quantity_delta",
                    "reason",
                    "note",
                ]
                rows = self._stock_rows
            elif mode == "detail":
                fieldnames = [
                    "sale_id",
                    "sale_date",
                    "rep_id",
                    "rep_name",
                    "area_id",
                    "area_name",
                    "customer_id",
                    "customer_name",
                    "product_id",
                    "product_name",
                    "company",
                    "batch",
                    "mrp",
                    "trade_price",
                    "quantity",
                    "line_discount",
                    "line_net",
                    "sale_total_qty",
                    "sale_total_discount",
                    "sale_net_amount",
                ]
                rows = self._detail_rows
            elif mode == "rep":
                fieldnames = [
                    "rep_id",
                    "rep_name",
                    "bills",
                    "quantity",
                    "line_discount",
                    "net_sales",
                    "benefit_8pct",
                ]
                rows = aggregate_by_rep(self._detail_rows)
            elif mode == "area":
                fieldnames = [
                    "area_id",
                    "area_name",
                    "bills",
                    "quantity",
                    "line_discount",
                    "net_sales",
                    "benefit_8pct",
                ]
                rows = aggregate_by_area(self._detail_rows)
            elif mode == "product":
                fieldnames = [
                    "product_id",
                    "product_name",
                    "company",
                    "bills",
                    "quantity",
                    "line_discount",
                    "net_sales",
                    "benefit_8pct",
                ]
                rows = aggregate_by_product(self._detail_rows)
            elif mode == "customer":
                fieldnames = [
                    "customer_id",
                    "customer_name",
                    "bills",
                    "quantity",
                    "line_discount",
                    "net_sales",
                    "benefit_8pct",
                ]
                rows = aggregate_by_customer(self._detail_rows)
            else:
                messagebox.showerror("Export", f"Unknown mode: {mode}")
                return

            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                w.writeheader()
                for row in rows:
                    out = dict(row)
                    if "sale_date" in out and out["sale_date"] is not None:
                        out["sale_date"] = str(out["sale_date"])
                    if "created_at" in out and out["created_at"] is not None:
                        out["created_at"] = str(out["created_at"])
                    w.writerow(out)

            messagebox.showinfo("Export", f"Saved:\n{path}")
        except OSError as exc:
            messagebox.showerror("Export failed", str(exc))

    def _export_pdf(self):
        mode = self._current_mode_key()
        if mode != "stock" and not self._detail_rows:
            messagebox.showinfo("Export", "Run a report first.")
            return

        path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf"), ("All", "*.*")],
            initialfile=f"report_{mode}.pdf",
        )
        if not path:
            return

        try:
            doc = SimpleDocTemplate(path, pagesize=landscape(A4), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
            elements = []
            styles = getSampleStyleSheet()
            
            elements.append(Paragraph(f"Pharma System Report — {mode.upper()}", styles['Heading1']))
            elements.append(Spacer(1, 10))
            
            headers = [self.tree.heading(c)["text"] for c in self.tree["columns"]]
            data = [headers]
            for child in self.tree.get_children():
                data.append([str(v) for v in self.tree.item(child)["values"]])
            
            col_widths = [(700 / len(headers))] * len(headers)
            t = Table(data, colWidths=col_widths, repeatRows=1)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2980b9")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 10),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,1), (-1,-1), 8),
                ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#bdc3c7"))
            ]))
            elements.append(t)
            doc.build(elements)
            messagebox.showinfo("Export", f"Saved PDF:\n{path}")
        except Exception as exc:
            messagebox.showerror("Export failed", str(exc))
