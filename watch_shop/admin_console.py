import json
import os

WATCHES_FILE = 'watches.json'
ORDERS_FILE = 'orders.json'

def load_data():
    """Загрузка данных"""
    watches = {}
    if os.path.exists(WATCHES_FILE):
        with open(WATCHES_FILE, 'r', encoding='utf-8') as f:
            watches = json.load(f)
    return watches

def save_data(watches):
    """Сохранение данных"""
    with open(WATCHES_FILE, 'w', encoding='utf-8') as f:
        json.dump(watches, f, ensure_ascii=False, indent=2)

def show_watches(watches):
    """Показать все часы"""
    print("\n" + "="*50)
    print("ТОВАРЫ В МАГАЗИНЕ:")
    for id, watch in watches.items():
        print(f"\nID: {id}")
        print(f"Название: {watch['name']}")
        print(f"Цена: {watch['price']} tenge.")
        print(f"В наличии: {watch['in_stock']}")

def add_watch(watches):
    """Добавить часы"""
    new_id = str(len(watches) + 1)
    name = input("Название: ")
    price = int(input("Цена: "))
    brand = input("Бренд: ")
    description = input("Описание: ")
    in_stock = int(input("Количество: "))
    
    watches[new_id] = {
        'name': name,
        'price': price,
        'brand': brand,
        'description': description,
        'in_stock': in_stock
    }
    print(f" Добавлено с ID {new_id}")

def main():
    watches = load_data()
    
    while True:
        print("\n" + "="*50)
        print("АДМИН-ПАНЕЛЬ")
        print("1. Показать товары")
        print("2. Добавить товар")
        print("3. Выход")
        
        choice = input("Выберите: ")
        
        if choice == '1':
            show_watches(watches)
        elif choice == '2':
            add_watch(watches)
        elif choice == '3':
            save_data(watches)
            print(" До свидания!")
            break

if __name__ == '__main__':
    main()