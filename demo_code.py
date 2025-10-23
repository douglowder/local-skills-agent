def calculate_discount(price, discount_percent):
    if discount_percent > 100:
        discount_percent = 100
    if discount_percent < 0:
        discount_percent = 0
    discount = price * (discount_percent / 100)
    return price - discount

def process_order(items):
    total = 0
    for item in items:
        if item['quantity'] > 0:
            total += item['price'] * item['quantity']
    return total
