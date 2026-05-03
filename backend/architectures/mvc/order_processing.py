"""
MVC Architecture - Order Processing System
Model-View-Controller separation of concerns.

Model: data structure and business rules
View: data formatting / serialization
Controller: orchestrates interaction between Model and View
"""


# ── Model ──────────────────────────────────────────────────────────────
TAX_RATE = 0.08
DISCOUNT_THRESHOLD = 500.0
DISCOUNT_RATE = 0.10


class OrderModel:
    """Model: encapsulates order state and business rules."""

    _store: dict = {}
    _next_id: int = 1

    @classmethod
    def reset(cls):
        cls._store = {}
        cls._next_id = 1

    @classmethod
    def create(cls, customer_name: str) -> dict:
        order = {
            "id": cls._next_id,
            "customer_name": customer_name,
            "items": [],
            "subtotal": 0.0,
            "tax": 0.0,
            "discount": 0.0,
            "total": 0.0,
            "status": "created",
            "payment_status": "pending",
        }
        cls._store[cls._next_id] = order
        cls._next_id += 1
        return order

    @classmethod
    def get(cls, order_id: int) -> dict | None:
        return cls._store.get(order_id)

    @classmethod
    def get_all(cls) -> list[dict]:
        return list(cls._store.values())

    @classmethod
    def add_item(cls, order_id: int, name: str, price: float, quantity: int) -> dict:
        order = cls.get(order_id)
        if order is None:
            raise ValueError(f"Order {order_id} not found")
        if price < 0:
            raise ValueError("Price cannot be negative")
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        order["items"].append({"name": name, "price": price, "quantity": quantity})
        cls._recalculate(order)
        return order

    @classmethod
    def _recalculate(cls, order: dict):
        subtotal = sum(i["price"] * i["quantity"] for i in order["items"])
        discount = subtotal * DISCOUNT_RATE if subtotal >= DISCOUNT_THRESHOLD else 0.0
        taxable = subtotal - discount
        tax = taxable * TAX_RATE
        order["subtotal"] = round(subtotal, 2)
        order["discount"] = round(discount, 2)
        order["tax"] = round(tax, 2)
        order["total"] = round(taxable + tax, 2)

    @classmethod
    def process_payment(cls, order_id: int, amount: float) -> dict:
        order = cls.get(order_id)
        if order is None:
            raise ValueError(f"Order {order_id} not found")
        if order["payment_status"] == "paid":
            raise ValueError("Order already paid")
        if amount < order["total"]:
            raise ValueError("Insufficient payment amount")
        order["payment_status"] = "paid"
        order["status"] = "confirmed"
        return order

    @classmethod
    def update_status(cls, order_id: int, status: str) -> dict:
        valid = ["created", "confirmed", "shipped", "delivered", "cancelled"]
        order = cls.get(order_id)
        if order is None:
            raise ValueError(f"Order {order_id} not found")
        if status not in valid:
            raise ValueError(f"Invalid status: {status}")
        order["status"] = status
        return order


# ── View ───────────────────────────────────────────────────────────────
class OrderView:
    """View: formats order data for presentation."""

    @staticmethod
    def render_order(order: dict) -> dict:
        return order

    @staticmethod
    def render_summary(order: dict) -> dict:
        return {
            "id": order["id"],
            "customer": order["customer_name"],
            "item_count": len(order["items"]),
            "total": order["total"],
            "status": order["status"],
            "payment": order["payment_status"],
        }

    @staticmethod
    def render_list(orders: list[dict]) -> list[dict]:
        return orders


# ── Controller ─────────────────────────────────────────────────────────
class OrderController:
    """Controller: handles requests and coordinates Model ↔ View."""

    def __init__(self):
        OrderModel.reset()
        self.view = OrderView()

    def create_order(self, customer_name: str) -> dict:
        order = OrderModel.create(customer_name)
        return self.view.render_order(order)

    def add_item(self, order_id: int, name: str, price: float, quantity: int) -> dict:
        order = OrderModel.add_item(order_id, name, price, quantity)
        return self.view.render_order(order)

    def process_payment(self, order_id: int, amount: float) -> dict:
        order = OrderModel.process_payment(order_id, amount)
        return self.view.render_order(order)

    def update_status(self, order_id: int, status: str) -> dict:
        order = OrderModel.update_status(order_id, status)
        return self.view.render_order(order)

    def get_order(self, order_id: int) -> dict:
        order = OrderModel.get(order_id)
        if order is None:
            raise ValueError(f"Order {order_id} not found")
        return self.view.render_order(order)

    def get_all_orders(self) -> list[dict]:
        return self.view.render_list(OrderModel.get_all())

    def get_order_summary(self, order_id: int) -> dict:
        order = OrderModel.get(order_id)
        if order is None:
            raise ValueError(f"Order {order_id} not found")
        return self.view.render_summary(order)
