import tkinter as tk
from tkinter import ttk, messagebox
from logic.profit_logic import calculate_total_profit
from logic.sales_logic import get_pending_credit_bills, mark_sale_paid
from data.database import SessionLocal
from data.models import Product, Rep, Area, Sale, Customer

class Dashboard(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#ecf0f1")

        title_frame = tk.Frame(self, bg="#ecf0f1")
        title_frame.pack(fill="x", pady=20)
        tk.Label(title_frame, text="Dashboard", font=("Arial", 24, "bold"), bg="#ecf0f1").pack(side="left", padx=20)

        self.stats_frame = tk.Frame(self, bg="#ecf0f1")
        self.stats_frame.pack(fill="x", padx=20, pady=10)

        self.credit_frame = tk.LabelFrame(self, text="Pending Credit Bills", bg="#ecf0f1")
        self.credit_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Build Credit Grid
        columns = ("ID", "Date", "Rep", "Customer", "Amount")
        self.credit_table = ttk.Treeview(self.credit_frame, columns=columns, show="headings", height=8)
        self.credit_table.heading("ID", text="Bill #")
        self.credit_table.heading("Date", text="Date")
        self.credit_table.heading("Rep", text="Rep")
        self.credit_table.heading("Customer", text="Customer")
        self.credit_table.heading("Amount", text="Total Amount")
        
        self.credit_table.column("ID", width=60, anchor="center")
        self.credit_table.column("Date", width=100)
        self.credit_table.column("Rep", width=150)
        self.credit_table.column("Customer", width=150)
        self.credit_table.column("Amount", width=100, anchor="e")

        vs = ttk.Scrollbar(self.credit_frame, orient="vertical", command=self.credit_table.yview)
        self.credit_table.configure(yscrollcommand=vs.set)
        
        btn_frame = tk.Frame(self.credit_frame, bg="#ecf0f1")
        btn_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        tk.Button(btn_frame, text="Mark as Paid", command=self._mark_paid, bg="#27ae60", fg="white", width=14).pack(pady=5)
        tk.Button(btn_frame, text="Refresh", command=self.refresh, bg="#2980b9", fg="white", width=14).pack(pady=5)
        
        self.credit_table.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        vs.pack(side="left", fill="y", pady=5)

        self.refresh()

    def refresh(self):
        # Clear stats
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
            
        stats = self.get_stats()
        for i, (label_text, value) in enumerate(stats.items()):
            row = i // 2
            col = (i % 2) * 2
            tk.Label(self.stats_frame, text=label_text + ":", width=22, anchor="w", font=("Arial", 14), bg="#ecf0f1").grid(row=row, column=col, pady=5, sticky="w")
            tk.Label(self.stats_frame, text=value, font=("Arial", 14, "bold"), bg="#ecf0f1", width=12, anchor="w").grid(row=row, column=col+1, pady=5, sticky="w")

        # Clear table
        for r in self.credit_table.get_children():
            self.credit_table.delete(r)

        # Load credits
        credits = get_pending_credit_bills()
        for c in credits:
            self.credit_table.insert("", "end", iid=str(c["id"]), values=(
                c["id"], c["date"], c["rep"], c["customer"], f"{c['net_amount']:.2f}"
            ))

    def get_stats(self):
        session = SessionLocal()
        try:
            total_sales = session.query(Sale).filter(Sale.payment_status == 'cash').count()
            unpaid_sales_count = session.query(Sale).filter(Sale.payment_status == 'credit').count()
            stats = {
                "Total Products": session.query(Product).count(),
                "Total Reps": session.query(Rep).count(),
                "Total Areas": session.query(Area).count(),
                "Total Customers": session.query(Customer).count(),
                "Total Paid Sales (bills)": total_sales,
                "Pending Credit Bills": unpaid_sales_count,
                "Total Profit (8% cash)": f"{calculate_total_profit():.2f}",
            }
            return stats
        finally:
            session.close()

    def _mark_paid(self):
        selected = self.credit_table.selection()
        if not selected:
            messagebox.showinfo("Wait", "Select a pending bill to mark as paid.", parent=self)
            return

        sale_id = int(selected[0])
        if messagebox.askyesno("Confirm", f"Mark Bill #{sale_id} as Paid? This will add it to your total financials.", parent=self):
            mark_sale_paid(sale_id)
            self.refresh()
