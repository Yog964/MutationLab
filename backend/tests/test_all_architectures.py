"""
Unified test suite that runs the same behavioral tests against every architecture.
Each architecture exposes an OrderController with the same interface:
  create_order, add_item, process_payment, update_status,
  get_order, get_all_orders, get_order_summary
"""
import pytest

from architectures.layered.order_processing import OrderController as LayeredController
from architectures.mvc.order_processing import OrderController as MvcController
from architectures.hexagonal.order_processing import OrderController as HexController
from architectures.microservices.order_processing import OrderController as MicroController
from architectures.event_driven.order_processing import OrderController as EventController


# Parametrize over all architectures so every test runs 5 times
@pytest.fixture(params=[
    LayeredController,
    MvcController,
    HexController,
    MicroController,
    EventController,
], ids=["layered", "mvc", "hexagonal", "microservices", "event_driven"])
def ctrl(request):
    return request.param()


# ── Creation Tests ─────────────────────────────────────────────────────
class TestOrderCreation:
    def test_create_order(self, ctrl):
        order = ctrl.create_order("Alice")
        assert order["customer_name"] == "Alice"
        assert order["status"] == "created"
        assert order["payment_status"] == "pending"
        assert order["total"] == 0.0

    def test_create_multiple_orders(self, ctrl):
        o1 = ctrl.create_order("Alice")
        o2 = ctrl.create_order("Bob")
        assert o1["id"] != o2["id"]


# ── Item Tests ─────────────────────────────────────────────────────────
class TestAddItem:
    def test_add_single_item(self, ctrl):
        order = ctrl.create_order("Alice")
        order = ctrl.add_item(order["id"], "Widget", 25.0, 2)
        assert len(order["items"]) == 1
        assert order["subtotal"] == 50.0

    def test_add_multiple_items(self, ctrl):
        order = ctrl.create_order("Alice")
        ctrl.add_item(order["id"], "Widget", 25.0, 2)
        order = ctrl.add_item(order["id"], "Gadget", 100.0, 1)
        assert len(order["items"]) == 2
        assert order["subtotal"] == 150.0

    def test_negative_price_rejected(self, ctrl):
        order = ctrl.create_order("Alice")
        with pytest.raises(ValueError, match="negative"):
            ctrl.add_item(order["id"], "Bad", -10.0, 1)

    def test_zero_quantity_rejected(self, ctrl):
        order = ctrl.create_order("Alice")
        with pytest.raises(ValueError, match="positive"):
            ctrl.add_item(order["id"], "Bad", 10.0, 0)

    def test_item_to_nonexistent_order(self, ctrl):
        with pytest.raises(ValueError, match="not found"):
            ctrl.add_item(999, "X", 10.0, 1)


# ── Calculation Tests ──────────────────────────────────────────────────
class TestCalculations:
    def test_tax_applied(self, ctrl):
        order = ctrl.create_order("Alice")
        order = ctrl.add_item(order["id"], "Item", 100.0, 1)
        # subtotal=100, no discount, tax=100*0.08=8
        assert order["tax"] == 8.0
        assert order["total"] == 108.0

    def test_discount_applied_above_threshold(self, ctrl):
        order = ctrl.create_order("Alice")
        order = ctrl.add_item(order["id"], "Expensive", 250.0, 3)
        # subtotal=750, discount=75, taxable=675, tax=54
        assert order["subtotal"] == 750.0
        assert order["discount"] == 75.0
        assert order["tax"] == 54.0
        assert order["total"] == 729.0

    def test_no_discount_below_threshold(self, ctrl):
        order = ctrl.create_order("Alice")
        order = ctrl.add_item(order["id"], "Cheap", 10.0, 2)
        assert order["discount"] == 0.0


# ── Payment Tests ──────────────────────────────────────────────────────
class TestPayment:
    def test_successful_payment(self, ctrl):
        order = ctrl.create_order("Alice")
        order = ctrl.add_item(order["id"], "Item", 100.0, 1)
        order = ctrl.process_payment(order["id"], 108.0)
        assert order["payment_status"] == "paid"
        assert order["status"] == "confirmed"

    def test_insufficient_payment(self, ctrl):
        order = ctrl.create_order("Alice")
        order = ctrl.add_item(order["id"], "Item", 100.0, 1)
        with pytest.raises(ValueError, match="Insufficient"):
            ctrl.process_payment(order["id"], 50.0)

    def test_double_payment(self, ctrl):
        order = ctrl.create_order("Alice")
        order = ctrl.add_item(order["id"], "Item", 100.0, 1)
        ctrl.process_payment(order["id"], 108.0)
        with pytest.raises(ValueError, match="already paid"):
            ctrl.process_payment(order["id"], 108.0)


# ── Status Tests ───────────────────────────────────────────────────────
class TestStatus:
    def test_update_status(self, ctrl):
        order = ctrl.create_order("Alice")
        order = ctrl.update_status(order["id"], "shipped")
        assert order["status"] == "shipped"

    def test_invalid_status(self, ctrl):
        order = ctrl.create_order("Alice")
        with pytest.raises(ValueError, match="Invalid status"):
            ctrl.update_status(order["id"], "exploded")


# ── Query Tests ────────────────────────────────────────────────────────
class TestQueries:
    def test_get_order(self, ctrl):
        order = ctrl.create_order("Alice")
        fetched = ctrl.get_order(order["id"])
        assert fetched["customer_name"] == "Alice"

    def test_get_nonexistent_order(self, ctrl):
        with pytest.raises(ValueError, match="not found"):
            ctrl.get_order(999)

    def test_get_all_orders(self, ctrl):
        ctrl.create_order("Alice")
        ctrl.create_order("Bob")
        assert len(ctrl.get_all_orders()) == 2

    def test_get_summary(self, ctrl):
        order = ctrl.create_order("Alice")
        ctrl.add_item(order["id"], "Item", 50.0, 2)
        summary = ctrl.get_order_summary(order["id"])
        assert summary["customer"] == "Alice"
        assert summary["item_count"] == 1
        assert "total" in summary
