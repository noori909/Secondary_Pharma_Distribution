from logic.sales_logic import record_sale
from logic.product_logic import add_product
from logic.rep_logic import add_rep
from logic.area_logic import add_area
from logic.profit_logic import calculate_total_profit, calculate_profit_by_rep, calculate_profit_by_area

# Setup minimal data
add_product("Panadol", "GSK", 50)
add_rep("Ali")
add_rep("Bilal")
add_area("North Zone")
add_area("South Zone")

# Record sales
record_sale(rep_id=1, area_id=1, product_id=1, quantity=10, net_amount=500)
record_sale(rep_id=2, area_id=2, product_id=1, quantity=5, net_amount=250)

print("Total profit:", calculate_total_profit())
print("Profit by rep 1:", calculate_profit_by_rep(1))
print("Profit by rep 2:", calculate_profit_by_rep(2))
print("Profit by area 1:", calculate_profit_by_area(1))
print("Profit by area 2:", calculate_profit_by_area(2))
