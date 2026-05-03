"""
Hexagonal Architecture (Ports & Adapters) - Order Processing System

Core domain is isolated from external concerns via Ports (interfaces)
and Adapters (implementations).

Ports:  OrderRepositoryPort (driven), OrderServicePort (driving)
Adapters: InMemoryOrderAdapter, OrderServiceAdapter
"""
from abc import ABC, abstractmethod

TAX_RATE = 0.08
DISCOUNT_THRESHOLD = 500.0
DISCOUNT_RATE = 0.10


# ── Domain Entity ──────────────────────────────────────────────────────
class Order:
    """Pure domain entity with no infrastructure dependencies."""

    def __init__(self, order_id: int, customer_name: str):
        self.id = order_id
        self.customer_name = customer_name
        self.items: list[dict] = []
        self.subtotal = 0.0
        self.tax = 0.0
        self.discount = 0.0
        self.total = 0.0
        self.status = "created"
        self.payment_status = "pending"

    def add_item(self, name: str, price: float, quantity: int):
        if price < 0:
            raise ValueError("Price cannot be negative")
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        self.items.append({"name": name, "price": price, "quantity": quantity})
        self._recalculate()

    def _recalculate(self):
        subtotal = sum(i["price"] * i["quantity"] for i in self.items)
        discount = subtotal * DISCOUNT_RATE if subtotal >= DISCOUNT_THRESHOLD else 0.0
        taxable = subtotal - discount
        tax = taxable * TAX_RATE
        self.subtotal = round(subtotal, 2)
        self.discount = round(discount, 2)
        self.tax = round(tax, 2)
        self.total = round(taxable + tax, 2)

    def process_payment(self, amount: float):
        if self.payment_status == "paid":
            raise ValueError("Order already paid")
        if amount < self.total:
            raise ValueError("Insufficient payment amount")
        self.payment_status = "paid"
        self.status = "confirmed"

    def update_status(self, status: str):
        valid = ["created", "confirmed", "shipped", "delivered", "cancelled"]
        if status not in valid:
            raise ValueError(f"Invalid status: {status}")
        self.status = status

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "items": self.items,
            "subtotal": self.subtotal,
            "tax": self.tax,
            "discount": self.discount,
            "total": self.total,
            "status": self.status,
            "payment_status": self.payment_status,
        }

    def summary(self) -> dict:
        return {
            "id": self.id,
            "customer": self.customer_name,
            "item_count": len(self.items),
            "total": self.total,
            "status": self.status,
            "payment": self.payment_status,
        }


# ── Port (driven side - repository interface) ─────────────────────────
class OrderRepositoryPort(ABC):
    @abstractmethod
    def save(self, order: Order) -> Order: ...
    @abstractmethod
    def find_by_id(self, order_id: int) -> Order | None: ...
    @abstractmethod
    def find_all(self) -> list[Order]: ...


# ── Adapter (driven side - in-memory implementation) ───────────────────
class InMemoryOrderAdapter(OrderRepositoryPort):
    def __init__(self):
        self._store: dict[int, Order] = {}

    def save(self, order: Order) -> Order:
        self._store[order.id] = order
        return order

    def find_by_id(self, order_id: int) -> Order | None:
        return self._store.get(order_id)

    def find_all(self) -> list[Order]:
        return list(self._store.values())


# ── Port (driving side - service interface) ────────────────────────────
class OrderServicePort(ABC):
    @abstractmethod
    def create_order(self, customer_name: str) -> dict: ...
    @abstractmethod
    def add_item(self, order_id: int, name: str, price: float, quantity: int) -> dict: ...
    @abstractmethod
    def process_payment(self, order_id: int, amount: float) -> dict: ...
    @abstractmethod
    def update_status(self, order_id: int, status: str) -> dict: ...
    @abstractmethod
    def get_order(self, order_id: int) -> dict: ...
    @abstractmethod
    def get_all_orders(self) -> list[dict]: ...
    @abstractmethod
    def get_order_summary(self, order_id: int) -> dict: ...


# ── Adapter (driving side - service implementation) ────────────────────
class OrderServiceAdapter(OrderServicePort):
    def __init__(self, repository: OrderRepositoryPort):
        self.repo = repository
        self._next_id = 1

    def create_order(self, customer_name: str) -> dict:
        order = Order(self._next_id, customer_name)
        self._next_id += 1
        self.repo.save(order)
        return order.to_dict()

    def add_item(self, order_id: int, name: str, price: float, quantity: int) -> dict:
        order = self.repo.find_by_id(order_id)
        if order is None:
            raise ValueError(f"Order {order_id} not found")
        order.add_item(name, price, quantity)
        self.repo.save(order)
        return order.to_dict()

    def process_payment(self, order_id: int, amount: float) -> dict:
        order = self.repo.find_by_id(order_id)
        if order is None:
            raise ValueError(f"Order {order_id} not found")
        order.process_payment(amount)
        self.repo.save(order)
        return order.to_dict()

    def update_status(self, order_id: int, status: str) -> dict:
        order = self.repo.find_by_id(order_id)
        if order is None:
            raise ValueError(f"Order {order_id} not found")
        order.update_status(status)
        self.repo.save(order)
        return order.to_dict()

    def get_order(self, order_id: int) -> dict:
        order = self.repo.find_by_id(order_id)
        if order is None:
            raise ValueError(f"Order {order_id} not found")
        return order.to_dict()

    def get_all_orders(self) -> list[dict]:
        return [o.to_dict() for o in self.repo.find_all()]

    def get_order_summary(self, order_id: int) -> dict:
        order = self.repo.find_by_id(order_id)
        if order is None:
            raise ValueError(f"Order {order_id} not found")
        return order.summary()


# ── Factory (wiring) ──────────────────────────────────────────────────
class OrderController:
    """Entry point that wires adapters together. Matches the interface of other architectures."""

    def __init__(self):
        repo = InMemoryOrderAdapter()
        self._service = OrderServiceAdapter(repo)

    def create_order(self, customer_name: str) -> dict:
        return self._service.create_order(customer_name)

    def add_item(self, order_id: int, name: str, price: float, quantity: int) -> dict:
        return self._service.add_item(order_id, name, price, quantity)

    def process_payment(self, order_id: int, amount: float) -> dict:
        return self._service.process_payment(order_id, amount)

    def update_status(self, order_id: int, status: str) -> dict:
        return self._service.update_status(order_id, status)

    def get_order(self, order_id: int) -> dict:
        return self._service.get_order(order_id)

    def get_all_orders(self) -> list[dict]:
        return self._service.get_all_orders()

    def get_order_summary(self, order_id: int) -> dict:
        return self._service.get_order_summary(order_id)
