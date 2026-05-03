"""
Event-Driven Architecture - Order Processing System

Uses an in-memory event bus. Components communicate exclusively
through events rather than direct method calls.

Components:
  - EventBus:       publish / subscribe infrastructure
  - OrderAggregate: domain model that emits events
  - OrderStore:     persists order state (in-memory)
  - Handlers:       react to events
  - OrderController: public API (publishes commands as events)
"""

TAX_RATE = 0.08
DISCOUNT_THRESHOLD = 500.0
DISCOUNT_RATE = 0.10


# ── Event Bus ──────────────────────────────────────────────────────────
class EventBus:
    """Simple in-memory publish/subscribe event bus."""

    def __init__(self):
        self._handlers: dict[str, list] = {}
        self.event_log: list[dict] = []

    def subscribe(self, event_type: str, handler):
        self._handlers.setdefault(event_type, []).append(handler)

    def publish(self, event_type: str, data: dict):
        self.event_log.append({"type": event_type, "data": data})
        for handler in self._handlers.get(event_type, []):
            handler(data)


# ── Order Store ────────────────────────────────────────────────────────
class OrderStore:
    """In-memory storage for order aggregates."""

    def __init__(self):
        self._orders: dict[int, dict] = {}
        self._next_id = 1

    def next_id(self) -> int:
        oid = self._next_id
        self._next_id += 1
        return oid

    def save(self, order: dict):
        self._orders[order["id"]] = order

    def get(self, order_id: int) -> dict | None:
        return self._orders.get(order_id)

    def get_all(self) -> list[dict]:
        return list(self._orders.values())


# ── Event Handlers ─────────────────────────────────────────────────────
class OrderEventHandlers:
    """Handles domain events and updates the store."""

    def __init__(self, store: OrderStore, bus: EventBus):
        self.store = store
        self.bus = bus
        self.notifications: list[str] = []

        bus.subscribe("OrderCreated", self.on_order_created)
        bus.subscribe("ItemAdded", self.on_item_added)
        bus.subscribe("PaymentProcessed", self.on_payment_processed)
        bus.subscribe("StatusUpdated", self.on_status_updated)

    def on_order_created(self, data: dict):
        self.store.save(data["order"])
        self.notifications.append(f"Order {data['order']['id']} created")

    def on_item_added(self, data: dict):
        order = self.store.get(data["order_id"])
        if order:
            order["items"] = data["items"]
            self._recalculate(order)
            self.store.save(order)

    def on_payment_processed(self, data: dict):
        order = self.store.get(data["order_id"])
        if order:
            order["payment_status"] = "paid"
            order["status"] = "confirmed"
            self.store.save(order)
            self.notifications.append(f"Payment for order {data['order_id']}")

    def on_status_updated(self, data: dict):
        order = self.store.get(data["order_id"])
        if order:
            order["status"] = data["status"]
            self.store.save(order)

    @staticmethod
    def _recalculate(order: dict):
        subtotal = sum(i["price"] * i["quantity"] for i in order["items"])
        discount = subtotal * DISCOUNT_RATE if subtotal >= DISCOUNT_THRESHOLD else 0.0
        taxable = subtotal - discount
        tax = taxable * TAX_RATE
        order["subtotal"] = round(subtotal, 2)
        order["discount"] = round(discount, 2)
        order["tax"] = round(tax, 2)
        order["total"] = round(taxable + tax, 2)


# ── Controller (command publisher) ─────────────────────────────────────
class OrderController:
    """Public API that issues commands via the event bus."""

    def __init__(self):
        self.bus = EventBus()
        self.store = OrderStore()
        self.handlers = OrderEventHandlers(self.store, self.bus)

    def create_order(self, customer_name: str) -> dict:
        order = {
            "id": self.store.next_id(),
            "customer_name": customer_name,
            "items": [],
            "subtotal": 0.0,
            "tax": 0.0,
            "discount": 0.0,
            "total": 0.0,
            "status": "created",
            "payment_status": "pending",
        }
        self.bus.publish("OrderCreated", {"order": order})
        return self.store.get(order["id"])

    def add_item(self, order_id: int, name: str, price: float, quantity: int) -> dict:
        order = self.store.get(order_id)
        if order is None:
            raise ValueError(f"Order {order_id} not found")
        if price < 0:
            raise ValueError("Price cannot be negative")
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        items = order["items"] + [{"name": name, "price": price, "quantity": quantity}]
        self.bus.publish("ItemAdded", {"order_id": order_id, "items": items})
        return self.store.get(order_id)

    def process_payment(self, order_id: int, amount: float) -> dict:
        order = self.store.get(order_id)
        if order is None:
            raise ValueError(f"Order {order_id} not found")
        if order["payment_status"] == "paid":
            raise ValueError("Order already paid")
        if amount < order["total"]:
            raise ValueError("Insufficient payment amount")
        self.bus.publish("PaymentProcessed", {"order_id": order_id, "amount": amount})
        return self.store.get(order_id)

    def update_status(self, order_id: int, status: str) -> dict:
        valid = ["created", "confirmed", "shipped", "delivered", "cancelled"]
        order = self.store.get(order_id)
        if order is None:
            raise ValueError(f"Order {order_id} not found")
        if status not in valid:
            raise ValueError(f"Invalid status: {status}")
        self.bus.publish("StatusUpdated", {"order_id": order_id, "status": status})
        return self.store.get(order_id)

    def get_order(self, order_id: int) -> dict:
        order = self.store.get(order_id)
        if order is None:
            raise ValueError(f"Order {order_id} not found")
        return order

    def get_all_orders(self) -> list[dict]:
        return self.store.get_all()

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
