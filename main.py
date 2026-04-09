from ui.main_app import PharmaApp
from data.init_db import init_db


def main() -> None:
    # Ensure SQLite tables exist before any UI screen queries them.
    init_db()
    app = PharmaApp()
    app.mainloop()


if __name__ == "__main__":
    main()
