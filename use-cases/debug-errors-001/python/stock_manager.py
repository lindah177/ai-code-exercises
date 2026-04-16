# stock_manager.py
def print_inventory_report(items):
    print("===== INVENTORY REPORT =====")
    for i in range(len(items)):
        print(f"Item {i+1}: {items[i]['name']} - Quantity: {items[i]['quantity']}")
    print("============================")

def main():
    items = [
        {"name": "Laptop", "quantity": 10},
        {"name": "Mouse", "quantity": 30},
        {"name": "Keyboard", "quantity": 15}
    ]
    print_inventory_report(items)

if __name__ == "__main__":
    main()