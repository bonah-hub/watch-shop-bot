carts = {}

def add_to_cart(user_id, watch_id, watch_data):
    if user_id not in carts:
        carts[user_id] = {}
    
    if watch_id in carts[user_id]:
        carts[user_id][watch_id]['quantity'] += 1
    else:
        carts[user_id][watch_id] = {
            'name': watch_data['name'],
            'price': watch_data['price'],
            'quantity': 1,
            'brand': watch_data['brand']
        }
    
    return carts[user_id][watch_id]['quantity']

def get_cart_total(user_id):
    if user_id not in carts:
        return 0
    
    total = 0
    for item in carts[user_id].values():
        total += item['price'] * item['quantity']
    return total

def get_cart_items(user_id):
    return carts.get(user_id, {})

def clear_cart(user_id):
    if user_id in carts:
        carts[user_id] = {}