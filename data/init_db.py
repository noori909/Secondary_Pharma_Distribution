from data.database import engine
from data.models import Base
from sqlalchemy import inspect, text


def _get_existing_columns(table_name):
    inspector = inspect(engine)
    if not inspector.has_table(table_name):
        return set()
    return {col["name"] for col in inspector.get_columns(table_name)}


def _add_column_if_missing(table_name, column_name, ddl_type):
    columns = _get_existing_columns(table_name)
    if column_name in columns:
        return
    with engine.begin() as conn:
        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl_type}"))


def init_db():
    Base.metadata.create_all(bind=engine)
    # Lightweight migrations for existing local SQLite files.
    _add_column_if_missing("products", "batch", "VARCHAR")
    _add_column_if_missing("products", "formula", "VARCHAR")
    _add_column_if_missing("products", "description", "VARCHAR")
    _add_column_if_missing("sales", "customer_id", "INTEGER")
    _add_column_if_missing("sales", "discount", "FLOAT DEFAULT 0")

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
