# tests/test_sales_workflow.py — Boss-proof version for Python 3.13

import sys
import os

# ------------------------------
# 1️⃣ Force project root into sys.path
# ------------------------------
# This ensures imports from logic/ and data/ always work
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# ------------------------------
# 2️⃣ Imports
# ------------------------------
from logic.product_logic import add_product, get_all_products
from logic.rep_logic import add_rep, get_all_reps, set_rep_status
from logic.area_logic import add_area, get_all_areas, set_area_status
from logic.sales_logic import record_sale, get_all_sales
from data.database import SessionLocal
from data.models import Rep, Area, Product

# ------------------------------
# 3️⃣ Add sample data
# ------------------------------
add_product("Panadol", "GSK", 50)
add_rep("Ali")
add_area("North Zone")

# ------------------------------
# 4️⃣ Fetch dynamic IDs
# ------------------------------
session = SessionLocal()

rep = session.query(Rep).filter(Rep.name == "Ali").first()
area = session.query(Area).filter(Area.name == "North Zone").first()
product = session.query(Product).filter(Product.name == "Panadol").first()

rep_id = rep.id
area_id = area.id
product_id = product.id

session.close()

print(f"Rep ID: {rep_id}, Area ID: {area_id}, Product ID: {product_id}")

# ------------------------------
# 5️⃣ Record a sale
# ------------------------------
record_sale(
    rep_id=rep_id,
    area_id=area_id,
    product_id=product_id,
    quantity=10,
    net_amount=500
)

# ------------------------------
# 6️⃣ Fetch and print sales
# ------------------------------
sales = get_all_sales()

print("\n=== ALL SALES ===")
for s in sales:
    print(
        f"Sale ID: {s.id}, Date: {s.date}, "
        f"Rep ID: {s.rep_id}, Area ID: {s.area_id}, Product ID: {s.product_id}, "
        f"Quantity: {s.quantity}, Net: {s.net_amount}"
    )

# ------------------------------
# 7️⃣ Print products, reps, areas
# ------------------------------
print("\n=== ALL PRODUCTS ===")
for p in get_all_products():
    print(f"ID: {p.id}, Name: {p.name}, Company: {p.company}, Price: {p.trade_price}")

print("\n=== ALL REPS ===")
for r in get_all_reps():
    print(f"ID: {r.id}, Name: {r.name}, Status: {r.status}")

print("\n=== ALL AREAS ===")
for a in get_all_areas():
    print(f"ID: {a.id}, Name: {a.name}, Status: {a.status}")
