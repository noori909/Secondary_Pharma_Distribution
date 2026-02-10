import tkinter as tk

# Import all screens
from ui.dashboard import Dashboard
from ui.products_ui import ProductsUI
from ui.reps_ui import RepsUI
from ui.areas_ui import AreasUI
from ui.sales_ui import SalesUI


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
            "Sales": SalesUI
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

    # ---- SHOW SCREEN FUNCTION ----
    def show_screen(self, screen_class):
        if self.current_screen:
            self.current_screen.destroy()  # Remove old screen
        self.current_screen = screen_class(self.container)
        self.current_screen.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = PharmaApp()
    app.mainloop()
