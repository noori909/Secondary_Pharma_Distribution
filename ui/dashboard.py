import tkinter as tk
from logic.profit_logic import calculate_total_profit
from data.database import SessionLocal
from data.models import Product, Rep, Area, Sale


class Dashboard(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#ecf0f1")

        tk.Label(
            self,
            text="Dashboard",
            font=("Arial", 24, "bold"),
            bg="#ecf0f1"
        ).pack(pady=20)

        stats = self.get_stats()

        for label, value in stats.items():
            row = tk.Frame(self, bg="#ecf0f1")
            row.pack(pady=10)

            tk.Label(row, text=label + ":", width=20, anchor="w",
                     font=("Arial", 14), bg="#ecf0f1").pack(side="left")
            tk.Label(row, text=value,
                     font=("Arial", 14, "bold"), bg="#ecf0f1").pack(side="left")

    def get_stats(self):
        session = SessionLocal()

        stats = {
            "Total Products": session.query(Product).count(),
            "Total Reps": session.query(Rep).count(),
            "Total Areas": session.query(Area).count(),
            "Total Sales": session.query(Sale).count(),
            "Total Profit (8%)": f"{calculate_total_profit():.2f}"
        }

        session.close()
        return stats
