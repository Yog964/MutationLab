"""
Layered Architecture - Order Processing System
Layers: Presentation -> Business Logic -> Data Access

This architecture separates concerns into distinct horizontal layers,
where each layer only communicates with the layer directly below it.
"""


# ── Data Access Layer ──────────────────────────────────────────────────
class OrderRepository:
    """Data Access Layer: handles storage and retrieval of orders."""

    def __init__(self):
        self._orders = {}
        self._next_id = 1

    def save(self, order_data: dict) -> dict:
        order_id = self._next_id
        self._next_id += 1
        order_data["id"] = order_id
        self._orders[order_id] = order_data
        return order_data

    def find_by_id(self, order_id: int) -> dict | None:
        return self._orders.get(order_id)

    def find_all(self) -> list[dict]:
        return list(self._orders.values())

    def update(self, order_id: int, order_data: dict) -> dict | None:
        if order_id in self._orders:
            self._orders[order_id] = order_data
            return order_data
        return None

    def delete(self, order_id: int) -> bool:
        if order_id in self._orders:
            del self._orders[order_id]
            return True
        return False


# ── Business Logic Layer ───────────────────────────────────────────────
TAX_RATE = 0.08
DISCOUNT_THRESHOLD = 500.0
DISCOUNT_RATE = 0.10


class OrderService:
    """Business Logic Layer: contains all order processing rules."""

    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def create_order(self, customer_name: str) -> dict:
        order_data = {
            "customer_name": customer_name,
            "items": [],
            "subtotal": 0.0,
            "tax": 0.0,
            "discount": 0.0,
            "total": 0.0,
            "status": "created",
            "payment_status": "pending",
        }
        return self.repository.save(order_data)

    def add_item(self, order_id: int, name: str, price: float, quantity: int) -> dict:
        order = self.repository.find_by_id(order_id)
        if order is None:
            raise ValueError(f"Order {order_id} not found")
        if price < 0:
            raise ValueError("Price cannot be negative")
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        item = {"name": name, "price": price, "quantity": quantity}
        order["items"].append(item)
        self._recalculate(order)
        self.repository.update(order_id, order)
        return order

    def _recalculate(self, order: dict):
        subtotal = sum(item["price"] * item["quantity"] for item in order["items"])
        discount = subtotal * DISCOUNT_RATE if subtotal >= DISCOUNT_THRESHOLD else 0.0
        taxable = subtotal - discount
        tax = taxable * TAX_RATE
        order["subtotal"] = round(subtotal, 2)
        order["discount"] = round(discount, 2)
        order["tax"] = round(tax, 2)
        order["total"] = round(taxable + tax, 2)

    def process_payment(self, order_id: int, amount: float) -> dict:
        order = self.repository.find_by_id(order_id)
        if order is None:
            raise ValueError(f"Order {order_id} not found")
        if order["payment_status"] == "paid":
            raise ValueError("Order already paid")
        if amount < order["total"]:
            raise ValueError("Insufficient payment amount")
        order["payment_status"] = "paid"
        order["status"] = "confirmed"
        self.repository.update(order_id, order)
        return order

    def update_status(self, order_id: int, status: str) -> dict:
        valid_statuses = ["created", "confirmed", "shipped", "delivered", "cancelled"]
        order = self.repository.find_by_id(order_id)
        if order is None:
            raise ValueError(f"Order {order_id} not found")
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}")
        order["status"] = status
        self.repository.update(order_id, order)
        return order

    def get_order(self, order_id: int) -> dict:
        order = self.repository.find_by_id(order_id)
        if order is None:
            raise ValueError(f"Order {order_id} not found")
        return order

    def get_all_orders(self) -> list[dict]:
        return self.repository.find_all()

    def get_order_summary(self, order_id: int) -> dict:
        order = self.get_order(order_id)
        return {
            "id": order["id"],
            "customer": order["customer_name"],
            "item_count": len(order["items"]),
            "total": order["total"],
            "status": order["status"],
            "payment": order["payment_status"],
        }


# ── Presentation Layer ─────────────────────────────────────────────────
class OrderController:
    """Presentation Layer: thin wrapper that delegates to the service."""

    def __init__(self):
        self.service = OrderService(OrderRepository())

    def create_order(self, customer_name: str) -> dict:
        return self.service.create_order(customer_name)

    def add_item(self, order_id: int, name: str, price: float, quantity: int) -> dict:
        return self.service.add_item(order_id, name, price, quantity)

    def process_payment(self, order_id: int, amount: float) -> dict:
        return self.service.process_payment(order_id, amount)

    def update_status(self, order_id: int, status: str) -> dict:
        return self.service.update_status(order_id, status)

    def get_order(self, order_id: int) -> dict:
        return self.service.get_order(order_id)

    def get_all_orders(self) -> list[dict]:
        return self.service.get_all_orders()

    def get_order_summary(self, order_id: int) -> dict:
        return self.service.get_order_summary(order_id)
