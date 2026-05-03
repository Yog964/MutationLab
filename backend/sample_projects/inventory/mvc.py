# Inventory — MVC Architecture
class InventoryModel:
    def __init__(self):
        self.products = {}; self._next_id = 1
    def create(self, name, price, quantity):
        if price < 0: raise ValueError("Price cannot be negative")
        if quantity <= 0: raise ValueError("Quantity cannot be negative")
        pid = self._next_id; self._next_id += 1
        self.products[pid] = {"id": pid, "name": name, "price": price, "quantity": quantity}; return pid
    def find(self, pid):
        p = self.products.get(pid)
        if not p: raise ValueError("Product not found")
        return p
    def delete(self, pid):
        self.find(pid); del self.products[pid]; return True
    def all(self): return list(self.products.values())

class InventoryView:
    def format(self, product): return dict(product)

class InventoryController:
    def __init__(self):
        self.model = InventoryModel(); self.view = InventoryView()
    def add_product(self, name, price, qty): return self.model.create(name, price, qty)
    def remove_product(self, pid): return self.model.delete(pid)
    def update_quantity(self, pid, amount):
        p = self.model.find(pid); new_qty = p["quantity"] + amount
        if new_qty < 0: raise ValueError("Insufficient stock")
        p["quantity"] = new_qty; return new_qty
    def get_total_value(self):
        return sum(p["price"] * p["quantity"] for p in self.model.all())
    def is_in_stock(self, pid): return self.model.find(pid)["quantity"] > 0
    def apply_discount(self, pid, percent):
        if percent < 0 or percent > 100: raise ValueError("Invalid percent")
        p = self.model.find(pid); p["price"] = p["price"] * (100 - percent) / 100; return p["price"]
    def count_low_stock(self, threshold):
        return sum(1 for p in self.model.all() if p["quantity"] < threshold)
    def get_product(self, pid): return dict(self.model.find(pid))
    def search_by_price(self, lo, hi):
        return [p for p in self.model.all() if lo <= p["price"] <= hi]
