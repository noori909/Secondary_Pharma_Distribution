from logic.product_logic import get_all_products

products = get_all_products()

for p in products:
    print(p.id, p.name, p.company, p.trade_price, p.status)
