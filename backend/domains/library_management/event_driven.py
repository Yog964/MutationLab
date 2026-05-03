"""
Event-Driven Architecture — Library Management System
In-memory event bus with publish/subscribe.
"""

FINE_PER_DAY = 2.0
MAX_BORROW_DAYS = 14


class EventBus:
    def __init__(self):
        self._handlers: dict[str, list] = {}
        self.event_log: list[dict] = []

    def subscribe(self, event_type, handler):
        self._handlers.setdefault(event_type, []).append(handler)

    def publish(self, event_type, data):
        self.event_log.append({"type": event_type, "data": data})
        for h in self._handlers.get(event_type, []):
            h(data)


class BookStore:
    def __init__(self):
        self._books: dict[int, dict] = {}
        self._next_id = 1

    def next_id(self):
        bid = self._next_id; self._next_id += 1; return bid

    def save(self, book):
        self._books[book["id"]] = book

    def get(self, bid):
        return self._books.get(bid)

    def get_all(self):
        return list(self._books.values())


class LibraryEventHandlers:
    def __init__(self, store: BookStore, bus: EventBus):
        self.store = store
        bus.subscribe("BookAdded", self.on_added)
        bus.subscribe("BookIssued", self.on_issued)
        bus.subscribe("BookReturned", self.on_returned)
        self.last_fine = 0.0

    def on_added(self, data):
        self.store.save(data["book"])

    def on_issued(self, data):
        b = self.store.get(data["bid"])
        if b:
            b["available_copies"] -= 1
            b["issued_to"].append({"member": data["member"], "days": data["days"]})
            b["status"] = "available" if b["available_copies"] > 0 else "all_issued"
            self.store.save(b)

    def on_returned(self, data):
        b = self.store.get(data["bid"])
        if b:
            rec = next((r for r in b["issued_to"] if r["member"] == data["member"]), None)
            if rec:
                b["issued_to"].remove(rec)
                b["available_copies"] += 1
                b["status"] = "available"
                allowed = rec.get("days", MAX_BORROW_DAYS)
                self.last_fine = round(max(0, data["days_kept"] - allowed) * FINE_PER_DAY, 2)
                self.store.save(b)


class LibraryController:
    def __init__(self):
        self.bus = EventBus()
        self.store = BookStore()
        self.handlers = LibraryEventHandlers(self.store, self.bus)

    def add_book(self, title, author, copies=1):
        if not title or not title.strip(): raise ValueError("Book title cannot be empty")
        if not author or not author.strip(): raise ValueError("Author name cannot be empty")
        if copies < 1: raise ValueError("Copies must be at least 1")
        book = {
            "id": self.store.next_id(), "title": title.strip(), "author": author.strip(),
            "total_copies": copies, "available_copies": copies,
            "issued_to": [], "status": "available",
        }
        self.bus.publish("BookAdded", {"book": book})
        return self.store.get(book["id"])

    def issue_book(self, bid, member, days=MAX_BORROW_DAYS):
        b = self.store.get(bid)
        if b is None: raise ValueError(f"Book {bid} not found")
        if b["available_copies"] <= 0: raise ValueError("No copies available")
        if not member or not member.strip(): raise ValueError("Member name cannot be empty")
        self.bus.publish("BookIssued", {"bid": bid, "member": member.strip(), "days": days})
        return self.store.get(bid)

    def return_book(self, bid, member, days_kept):
        b = self.store.get(bid)
        if b is None: raise ValueError(f"Book {bid} not found")
        rec = next((r for r in b["issued_to"] if r["member"] == member.strip()), None)
        if rec is None: raise ValueError(f"No issue record for member '{member}'")
        self.bus.publish("BookReturned", {"bid": bid, "member": member.strip(), "days_kept": days_kept})
        return {"book": self.store.get(bid), "fine": self.handlers.last_fine}

    @staticmethod
    def calculate_fine(days_kept, allowed=MAX_BORROW_DAYS):
        if days_kept <= allowed: return 0.0
        return round((days_kept - allowed) * FINE_PER_DAY, 2)

    def check_availability(self, bid):
        b = self.store.get(bid)
        if b is None: raise ValueError(f"Book {bid} not found")
        return b["available_copies"] > 0

    def get_book_status(self, bid):
        b = self.store.get(bid)
        if b is None: raise ValueError(f"Book {bid} not found")
        return {
            "id": b["id"], "title": b["title"], "author": b["author"],
            "total_copies": b["total_copies"], "available_copies": b["available_copies"],
            "issued_count": len(b["issued_to"]), "status": b["status"],
        }

    def get_book(self, bid):
        b = self.store.get(bid)
        if b is None: raise ValueError(f"Book {bid} not found")
        return b

    def get_all_books(self):
        return self.store.get_all()
