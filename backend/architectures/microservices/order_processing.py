"""
Microservices Architecture - Order Processing System

Simulates independent micro-services communicating over synchronous
in-process calls (lightweight local simulation, not cloud-based).

Services:
  - OrderService:    manages order lifecycle
  - InventoryService: validates items (simulated)
  - PaymentService:  processes payments
  - NotificationService: sends notifications (simulated)
  - Gateway:         entry-point that routes to services
"""

TAX_RATE = 0.08
DISCOUNT_THRESHOLD = 500.0
DISCOUNT_RATE = 0.10


# ── Inventory Service ──────────────────────────────────────────────────
class InventoryService:
    """Simulates item validation and availability checking."""

    def validate_item(self, name: str, price: float, quantity: int) -> bool:
        if price < 0:
            raise ValueError("Price cannot be negative")
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        return True


# ── Payment Service ────────────────────────────────────────────────────
class PaymentService:
    """Processes payments independently."""

    def process(self, order_total: float, amount: float) -> dict:
        if amount < order_total:
            raise ValueError("Insufficient payment amount")
        return {"status": "success", "charged": order_total}


# ── Notification Service ───────────────────────────────────────────────
class NotificationService:
    """Simulates sending notifications."""

    def __init__(self):
        self.log: list[str] = []

    def send(self, message: str):
        self.log.append(message)


# ── Order Service ──────────────────────────────────────────────────────
class OrderService:
    """Core order management micro-service."""

    def __init__(self):
        self._orders: dict[int, dict] = {}
        self._next_id = 1

    def create(self, customer_name: str) -> dict:
        order = {
            "id": self._next_id,
            "customer_name": customer_name,
            "items": [],
            "subtotal": 0.0,
            "tax": 0.0,
            "discount": 0.0,
            "total": 0.0,
            "status": "created",
            "payment_status": "pending",
        }
        self._orders[self._next_id] = order
        self._next_id += 1
        return order

    def get(self, order_id: int) -> dict:
        order = self._orders.get(order_id)
        if order is None:
            raise ValueError(f"Order {order_id} not found")
        return order

    def get_all(self) -> list[dict]:
        return list(self._orders.values())

    def add_item(self, order_id: int, item: dict) -> dict:
        order = self.get(order_id)
        order["items"].append(item)
        self._recalculate(order)
        return order

    def _recalculate(self, order: dict):
        subtotal = sum(i["price"] * i["quantity"] for i in order["items"])
        discount = subtotal * DISCOUNT_RATE if subtotal >= DISCOUNT_THRESHOLD else 0.0
        taxable = subtotal - discount
        tax = taxable * TAX_RATE
        order["subtotal"] = round(subtotal, 2)
        order["discount"] = round(discount, 2)
        order["tax"] = round(tax, 2)
        order["total"] = round(taxable + tax, 2)

    def mark_paid(self, order_id: int) -> dict:
        order = self.get(order_id)
        if order["payment_status"] == "paid":
            raise ValueError("Order already paid")
        order["payment_status"] = "paid"
        order["status"] = "confirmed"
        return order

    def update_status(self, order_id: int, status: str) -> dict:
        valid = ["created", "confirmed", "shipped", "delivered", "cancelled"]
        order = self.get(order_id)
        if status not in valid:
            raise ValueError(f"Invalid status: {status}")
        order["status"] = status
        return order

    def summary(self, order_id: int) -> dict:
        order = self.get(order_id)
        return {
            "id": order["id"],
            "customer": order["customer_name"],
            "item_count": len(order["items"]),
            "total": order["total"],
            "status": order["status"],
            "payment": order["payment_status"],
        }


# ── API Gateway (orchestrator) ─────────────────────────────────────────
class OrderController:
    """Gateway that coordinates calls across micro-services."""

    def __init__(self):
        self.order_svc = OrderService()
        self.inventory_svc = InventoryService()
        self.payment_svc = PaymentService()
        self.notification_svc = NotificationService()

    def create_order(self, customer_name: str) -> dict:
        order = self.order_svc.create(customer_name)
        self.notification_svc.send(f"Order {order['id']} created for {customer_name}")
        return order

    def add_item(self, order_id: int, name: str, price: float, quantity: int) -> dict:
        self.inventory_svc.validate_item(name, price, quantity)
        item = {"name": name, "price": price, "quantity": quantity}
        order = self.order_svc.add_item(order_id, item)
        return order

    def process_payment(self, order_id: int, amount: float) -> dict:
        order = self.order_svc.get(order_id)
        self.payment_svc.process(order["total"], amount)
        order = self.order_svc.mark_paid(order_id)
        self.notification_svc.send(f"Payment received for order {order_id}")
        return order

    def update_status(self, order_id: int, status: str) -> dict:
        order = self.order_svc.update_status(order_id, status)
        self.notification_svc.send(f"Order {order_id} status -> {status}")
        return order

    def get_order(self, order_id: int) -> dict:
        return self.order_svc.get(order_id)

    def get_all_orders(self) -> list[dict]:
        return self.order_svc.get_all()

    def get_order_summary(self, order_id: int) -> dict:
        return self.order_svc.summary(order_id)
