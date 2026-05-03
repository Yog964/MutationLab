# Inventory — Hexagonal Architecture
from abc import ABC, abstractmethod

class InventoryPort(ABC):
    @abstractmethod
    def save(self, product): ...
    @abstractmethod
    def find(self, pid): ...
    @abstractmethod
    def remove(self, pid): ...
    @abstractmethod
    def all(self): ...

class InMemoryAdapter(InventoryPort):
    def __init__(self): self.store = {}; self._nid = 1
    def save(self, product):
        pid = self._nid; self._nid += 1
        product["id"] = pid; self.store[pid] = product; return pid
    def find(self, pid): return self.store.get(pid)
    def remove(self, pid):
        if pid in self.store: del self.store[pid]; return True
        return False
    def all(self): return list(self.store.values())

class InventoryUseCase:
    def __init__(self, adapter: InventoryPort): self.adapter = adapter
    def add_product(self, name, price, qty):
        if price < 0: raise ValueError("Price cannot be negative")
        if qty < 0: raise ValueError("Quantity cannot be negative")
        return self.adapter.save({"name": name, "price": price, "quantity": qty})
    def remove_product(self, pid):
        if not self.adapter.find(pid): raise ValueError("Product not found")
        return self.adapter.remove(pid)
    def update_quantity(self, pid, amount):
        p = self.adapter.find(pid)
        if not p: raise ValueError("Product not found")
        new_qty = p["quantity"] + amount
        if new_qty < 0: raise ValueError("Insufficient stock")
        p["quantity"] = new_qty; return new_qty
    def get_total_value(self):
        return sum(p["price"] * p["quantity"] for p in self.adapter.all())
    def is_in_stock(self, pid):
        p = self.adapter.find(pid)
        if not p: raise ValueError("Product not found")
        return p["quantity"] > 0
    def apply_discount(self, pid, pct):
        if pct < 0 or pct > 100: raise ValueError("Invalid percent")
        p = self.adapter.find(pid)
        if not p: raise ValueError("Product not found")
        p["price"] = p["price"] * (100 - pct) / 100; return p["price"]
    def count_low_stock(self, threshold):
        return sum(1 for p in self.adapter.all() if p["quantity"] < threshold)
    def get_product(self, pid):
        p = self.adapter.find(pid)
        if not p: raise ValueError("Product not found")
        return dict(p)
    def search_by_price(self, lo, hi):
        return [p for p in self.adapter.all() if lo <= p["price"] <= hi]

class InventoryController:
    def __init__(self): self.uc = InventoryUseCase(InMemoryAdapter())
    def add_product(self, name, price, qty): return self.uc.add_product(name, price, qty)
    def remove_product(self, pid): return self.uc.remove_product(pid)
    def update_quantity(self, pid, amt): return self.uc.update_quantity(pid, amt)
    def get_total_value(self): return self.uc.get_total_value()
    def is_in_stock(self, pid): return self.uc.is_in_stock(pid)
    def apply_discount(self, pid, pct): return self.uc.apply_discount(pid, pct)
    def count_low_stock(self, t): return self.uc.count_low_stock(t)
    def get_product(self, pid): return self.uc.get_product(pid)
    def search_by_price(self, lo, hi): return self.uc.search_by_price(lo, hi)
