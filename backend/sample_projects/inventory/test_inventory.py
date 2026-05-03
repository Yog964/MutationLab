import os, importlib, pytest
arch = os.environ.get('TEST_ARCH', 'layered')
mod = importlib.import_module(arch)
Controller = mod.InventoryController

class TestInventory:
    def setup_method(self): self.inv = Controller()

    def test_add_product(self):
        pid = self.inv.add_product("Widget", 10.0, 100)
        assert pid >= 1
    def test_add_negative_price(self):
        with pytest.raises(ValueError): self.inv.add_product("X", -5, 10)
    def test_add_negative_qty(self):
        with pytest.raises(ValueError): self.inv.add_product("X", 5, -10)
    def test_get_product(self):
        pid = self.inv.add_product("Bolt", 2.5, 50)
        p = self.inv.get_product(pid)
        assert p["name"] == "Bolt" and p["price"] == 2.5
    def test_remove_product(self):
        pid = self.inv.add_product("Nut", 1.0, 200)
        assert self.inv.remove_product(pid) is True
    def test_remove_invalid(self):
        with pytest.raises(ValueError): self.inv.remove_product(9999)
    def test_update_quantity_add(self):
        pid = self.inv.add_product("Screw", 0.5, 100)
        assert self.inv.update_quantity(pid, 50) == 150
    def test_update_quantity_subtract(self):
        pid = self.inv.add_product("Nail", 0.1, 100)
        assert self.inv.update_quantity(pid, -30) == 70
    def test_update_insufficient(self):
        pid = self.inv.add_product("Wire", 3.0, 10)
        with pytest.raises(ValueError): self.inv.update_quantity(pid, -20)
    def test_total_value(self):
        self.inv.add_product("A", 10, 5)
        self.inv.add_product("B", 20, 3)
        assert self.inv.get_total_value() == 110
    def test_in_stock_true(self):
        pid = self.inv.add_product("X", 5, 10)
        assert self.inv.is_in_stock(pid) is True
    def test_in_stock_false(self):
        pid = self.inv.add_product("Y", 5, 0)
        assert self.inv.is_in_stock(pid) is False
    def test_apply_discount(self):
        pid = self.inv.add_product("Z", 100, 1)
        new_price = self.inv.apply_discount(pid, 20)
        assert new_price == 80.0
    def test_discount_invalid(self):
        pid = self.inv.add_product("W", 50, 1)
        with pytest.raises(ValueError): self.inv.apply_discount(pid, 110)
    def test_count_low_stock(self):
        self.inv.add_product("A", 1, 5)
        self.inv.add_product("B", 1, 15)
        self.inv.add_product("C", 1, 3)
        assert self.inv.count_low_stock(10) == 2
    def test_search_by_price(self):
        self.inv.add_product("Cheap", 5, 1)
        self.inv.add_product("Mid", 50, 1)
        self.inv.add_product("Pricey", 200, 1)
        result = self.inv.search_by_price(10, 100)
        assert len(result) == 1
