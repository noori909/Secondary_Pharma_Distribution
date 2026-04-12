import tkinter as tk
import threading

# Import all screens
from ui.dashboard import Dashboard
from ui.products_ui import ProductsUI
from ui.reps_ui import RepsUI
from ui.areas_ui import AreasUI
from ui.customers_ui import CustomersUI
from ui.sales_ui import SalesUI
from ui.reports_ui import ReportsUI
from ui.stock_ui import StockUI


class PharmaApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Pharma Distribution System")
        self.geometry("1000x600")
        self.resizable(False, False)

        # ---- SIDEBAR ----
        sidebar = tk.Frame(self, width=200, bg="#2c3e50")
        sidebar.pack(side="left", fill="y")

        # ---- MAIN AREA ----
        self.container = tk.Frame(self, bg="#ecf0f1")
        self.container.pack(side="right", fill="both", expand=True)

        # ---- BUTTONS ----
        self.screens = {
            "Dashboard": Dashboard,
            "Products": ProductsUI,
            "Reps": RepsUI,
            "Areas": AreasUI,
            "Customers": CustomersUI,
            "Sales": SalesUI,
            "Stock": StockUI,
            "Reports": ReportsUI,
        }

        for name, screen_class in self.screens.items():
            btn = tk.Button(
                sidebar,
                text=name,
                fg="white",
                bg="#34495e",
                relief="flat",
                height=2,
                command=lambda sc=screen_class: self.show_screen(sc)
            )
            btn.pack(fill="x", padx=10, pady=5)

        self.current_screen = None
        self.show_screen(Dashboard)  # Show dashboard by default
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Start 10 PM daily backup + email scheduler in background
        try:
            from services.scheduler import start_scheduler
            start_scheduler()
        except Exception as e:
            print(f"Scheduler failed to start: {e}")

    def on_closing(self):
        """Show a status message and perform backup before closing."""
        # Create a tiny status window
        status_win = tk.Toplevel(self)
        status_win.title("Status")
        status_win.geometry("300x100")
        # Center it
        x = self.winfo_x() + (self.winfo_width() // 2) - 150
        y = self.winfo_y() + (self.winfo_height() // 2) - 50
        status_win.geometry(f"+{x}+{y}")
        status_win.resizable(False, False)
        status_win.overrideredirect(True) # Remove borders
        
        tk.Label(status_win, text="Performing End-of-Day Backup...", font=("Arial", 10, "bold"), pady=10).pack()
        tk.Label(status_win, text="Please wait — syncing to cloud...", font=("Arial", 9)).pack()
        
        status_win.update() # Force drawing
        self.withdraw()     # Hide main window

        def _do_work():
            try:
                from logic.backup_logic import perform_automated_backup
                perform_automated_backup()
            except Exception as e:
                print(f"Final backup failed: {e}")
            finally:
                self.quit() # Stop the mainloop

        # Run in thread so the status window can stay 'alive' (even though it's not interactive)
        threading.Thread(target=_do_work, daemon=False).start()

    # ---- SHOW SCREEN FUNCTION ----
    def show_screen(self, screen_class):
        if self.current_screen:
            self.current_screen.destroy()  # Remove old screen
        self.current_screen = screen_class(self.container)
        self.current_screen.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = PharmaApp()
    app.mainloop()
