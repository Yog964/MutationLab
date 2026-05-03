# Inventory — Event-Driven Architecture
class EventBus:
    def __init__(self): self._h = {}; self.log = []
    def on(self, evt, fn): self._h.setdefault(evt, []).append(fn)
    def emit(self, evt, data):
        self.log.append({"event": evt, "data": data})
        for fn in self._h.get(evt, []): fn(data)

class InventoryStore:
    def __init__(self, bus):
        self.bus = bus; self.products = {}; self._nid = 1
        bus.on("add_product", self._on_add)
        bus.on("remove_product", self._on_remove)
    def _on_add(self, d):
        if d["price"] < 0: raise ValueError("Price cannot be negative")
        if d["qty"] < 0: raise ValueError("Quantity cannot be negative")
        pid = self._nid; self._nid += 1
        self.products[pid] = {"id": pid, "name": d["name"], "price": d["price"], "quantity": d["qty"]}
        self.bus.emit("product_added", {"id": pid})
    def _on_remove(self, d):
        pid = d["id"]
        if pid not in self.products: raise ValueError("Product not found")
        del self.products[pid]

class InventoryController:
    def __init__(self):
        self.bus = EventBus(); self.store = InventoryStore(self.bus)
    def add_product(self, name, price, qty):
        self.store._on_add({"name": name, "price": price, "qty": qty})
        return self.store._nid - 1
    def remove_product(self, pid):
        self.store._on_remove({"id": pid}); return True
    def update_quantity(self, pid, amount):
        p = self.store.products.get(pid)
        if not p: raise ValueError("Product not found")
        nq = p["quantity"] + amount
        if nq < 0: raise ValueError("Insufficient stock")
        p["quantity"] = nq; return nq
    def get_total_value(self):
        return sum(p["price"] * p["quantity"] for p in self.store.products.values())
    def is_in_stock(self, pid):
        p = self.store.products.get(pid)
        if not p: raise ValueError("Product not found")
        return p["quantity"] > 0
    def apply_discount(self, pid, pct):
        if pct < 0 or pct > 100: raise ValueError("Invalid percent")
        p = self.store.products.get(pid)
        if not p: raise ValueError("Product not found")
        p["price"] = p["price"] * (100 - pct) / 100; return p["price"]
    def count_low_stock(self, threshold):
        return sum(1 for p in self.store.products.values() if p["quantity"] < threshold)
    def get_product(self, pid):
        p = self.store.products.get(pid)
        if not p: raise ValueError("Product not found")
        return dict(p)
    def search_by_price(self, lo, hi):
        return [p for p in self.store.products.values() if lo <= p["price"] <= hi]
