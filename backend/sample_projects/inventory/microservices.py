# Inventory — Microservices Architecture
class CatalogService:
    def __init__(self): self.products = {}; self._nid = 1
    def add(self, name, price, qty):
        if price < 0: raise ValueError("Price cannot be negative")
        if qty < 0: raise ValueError("Quantity cannot be negative")
        pid = self._nid; self._nid += 1
        self.products[pid] = {"id": pid, "name": name, "price": price, "quantity": qty}; return pid
    def get(self, pid):
        p = self.products.get(pid)
        if not p: raise ValueError("Product not found")
        return p
    def remove(self, pid): self.get(pid); del self.products[pid]; return True
    def all(self): return list(self.products.values())

class StockService:
    def __init__(self, catalog): self.catalog = catalog
    def update(self, pid, amount):
        p = self.catalog.get(pid); nq = p["quantity"] + amount
        if nq < 0: raise ValueError("Insufficient stock")
        p["quantity"] = nq; return nq
    def in_stock(self, pid): return self.catalog.get(pid)["quantity"] > 0
    def low_count(self, threshold):
        return sum(1 for p in self.catalog.all() if p["quantity"] < threshold)

class PricingService:
    def __init__(self, catalog): self.catalog = catalog
    def total_value(self):
        return sum(p["price"] * p["quantity"] for p in self.catalog.all())
    def discount(self, pid, pct):
        if pct < 0 or pct > 100: raise ValueError("Invalid percent")
        p = self.catalog.get(pid); p["price"] = p["price"] * (100 - pct) / 100; return p["price"]
    def search(self, lo, hi):
        return [p for p in self.catalog.all() if lo <= p["price"] <= hi]

class InventoryController:
    def __init__(self):
        self.catalog = CatalogService()
        self.stock = StockService(self.catalog)
        self.pricing = PricingService(self.catalog)
    def add_product(self, name, price, qty): return self.catalog.add(name, price, qty)
    def remove_product(self, pid): return self.catalog.remove(pid)
    def update_quantity(self, pid, amt): return self.stock.update(pid, amt)
    def get_total_value(self): return self.pricing.total_value()
    def is_in_stock(self, pid): return self.stock.in_stock(pid)
    def apply_discount(self, pid, pct): return self.pricing.discount(pid, pct)
    def count_low_stock(self, t): return self.stock.low_count(t)
    def get_product(self, pid): return dict(self.catalog.get(pid))
    def search_by_price(self, lo, hi): return self.pricing.search(lo, hi)
