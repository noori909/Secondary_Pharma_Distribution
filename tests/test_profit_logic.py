import time

from logic.area_logic import add_area
from logic.product_logic import add_product
from logic.profit_logic import (
    calculate_profit_by_area,
    calculate_profit_by_rep,
    calculate_total_profit,
)
from logic.rep_logic import add_rep
from logic.sales_logic import record_sale
from data.database import SessionLocal
from data.models import Area, Product, Rep

TAG = f"pfl_{int(time.time())}"

add_product(f"Med-{TAG}", "GSK", 50, quantity=500)
add_rep(f"R1-{TAG}")
add_rep(f"R2-{TAG}")
add_area(f"A1-{TAG}")
add_area(f"A2-{TAG}")

session = SessionLocal()
product = session.query(Product).filter(Product.name == f"Med-{TAG}").one()
r1 = session.query(Rep).filter(Rep.name == f"R1-{TAG}").one()
r2 = session.query(Rep).filter(Rep.name == f"R2-{TAG}").one()
a1 = session.query(Area).filter(Area.name == f"A1-{TAG}").one()
a2 = session.query(Area).filter(Area.name == f"A2-{TAG}").one()
session.close()

record_sale(rep_id=r1.id, area_id=a1.id, product_id=product.id, quantity=10, discount=0)
record_sale(rep_id=r2.id, area_id=a2.id, product_id=product.id, quantity=5, discount=0)

print("Total profit:", calculate_total_profit())
print("Profit by rep 1:", calculate_profit_by_rep(r1.id))
print("Profit by rep 2:", calculate_profit_by_rep(r2.id))
print("Profit by area 1:", calculate_profit_by_area(a1.id))
print("Profit by area 2:", calculate_profit_by_area(a2.id))
