# Inventory — Layered Architecture
class InventoryRepository:
    def __init__(self):
        self.products = {}
        self._next_id = 1
    def save(self, product):
        pid = self._next_id; self._next_id += 1
        product["id"] = pid; self.products[pid] = product; return pid
    def get(self, pid):
        return self.products.get(pid)
    def delete(self, pid):
        if pid in self.products: del self.products[pid]; return True
        return False
    def get_all(self): return list(self.products.values())

class InventoryService:
    def __init__(self):
        self.repo = InventoryRepository()
    def add_product(self, name, price, quantity):
        if price < 0: raise ValueError("Price cannot be negative")
        if quantity < 0: raise ValueError("Quantity cannot be negative")
        return self.repo.save({"name": name, "price": price, "quantity": quantity})
    def remove_product(self, pid):
        if not self.repo.get(pid): raise ValueError("Product not found")
        return self.repo.delete(pid)
    def update_quantity(self, pid, amount):
        p = self.repo.get(pid)
        if not p: raise ValueError("Product not found")
        new_qty = p["quantity"] + amount
        if new_qty < 0: raise ValueError("Insufficient stock")
        p["quantity"] = new_qty; return new_qty
    def get_total_value(self):
        return sum(p["price"] * p["quantity"] for p in self.repo.get_all())
    def is_in_stock(self, pid):
        p = self.repo.get(pid)
        if not p: raise ValueError("Product not found")
        return p["quantity"] > 0
    def apply_discount(self, pid, percent):
        p = self.repo.get(pid)
        if not p: raise ValueError("Product not found")
        if percent < 0 or percent > 100: raise ValueError("Invalid percent")
        p["price"] = p["price"] * (100 - percent) / 100; return p["price"]
    def count_low_stock(self, threshold):
        return sum(1 for p in self.repo.get_all() if p["quantity"] < threshold)
    def get_product(self, pid):
        p = self.repo.get(pid)
        if not p: raise ValueError("Product not found")
        return dict(p)
    def search_by_price(self, min_p, max_p):
        return [p for p in self.repo.get_all() if min_p <= p["price"] <= max_p]

class InventoryController:
    def __init__(self): self.svc = InventoryService()
    def add_product(self, name, price, qty): return self.svc.add_product(name, price, qty)
    def remove_product(self, pid): return self.svc.remove_product(pid)
    def update_quantity(self, pid, amount): return self.svc.update_quantity(pid, amount)
    def get_total_value(self): return self.svc.get_total_value()
    def is_in_stock(self, pid): return self.svc.is_in_stock(pid)
    def apply_discount(self, pid, pct): return self.svc.apply_discount(pid, pct)
    def count_low_stock(self, threshold): return self.svc.count_low_stock(threshold)
    def get_product(self, pid): return self.svc.get_product(pid)
    def search_by_price(self, lo, hi): return self.svc.search_by_price(lo, hi)
