"""
Microservices Architecture — Library Management System
Independent services with gateway coordination.
"""

FINE_PER_DAY = 2.0
MAX_BORROW_DAYS = 14


# ── Catalog Service ────────────────────────────────────────────────────
class CatalogService:
    def __init__(self):
        self._books: dict[int, dict] = {}
        self._next_id = 1

    def add(self, title, author, copies) -> dict:
        b = {
            "id": self._next_id, "title": title.strip(), "author": author.strip(),
            "total_copies": copies, "available_copies": copies,
            "issued_to": [], "status": "available",
        }
        self._books[self._next_id] = b
        self._next_id += 1
        return b

    def get(self, bid) -> dict:
        b = self._books.get(bid)
        if b is None: raise ValueError(f"Book {bid} not found")
        return b

    def get_all(self) -> list[dict]:
        return list(self._books.values())


# ── Lending Service ────────────────────────────────────────────────────
class LendingService:
    def issue(self, book: dict, member: str, days: int):
        if book["available_copies"] <= 0: raise ValueError("No copies available")
        book["available_copies"] -= 1
        book["issued_to"].append({"member": member.strip(), "days": days})
        book["status"] = "available" if book["available_copies"] > 0 else "all_issued"

    def return_book(self, book: dict, member: str, days_kept: int) -> float:
        rec = next((r for r in book["issued_to"] if r["member"] == member.strip()), None)
        if rec is None: raise ValueError(f"No issue record for member '{member}'")
        book["issued_to"].remove(rec)
        book["available_copies"] += 1
        book["status"] = "available"
        return self.calculate_fine(days_kept, rec.get("days", MAX_BORROW_DAYS))

    @staticmethod
    def calculate_fine(days_kept, allowed=MAX_BORROW_DAYS) -> float:
        if days_kept <= allowed: return 0.0
        return round((days_kept - allowed) * FINE_PER_DAY, 2)


# ── Notification Service ───────────────────────────────────────────────
class NotificationService:
    def __init__(self): self.log: list[str] = []
    def send(self, msg): self.log.append(msg)


# ── Gateway / Controller ──────────────────────────────────────────────
class LibraryController:
    def __init__(self):
        self.catalog = CatalogService()
        self.lending = LendingService()
        self.notifier = NotificationService()

    def add_book(self, title, author, copies=1):
        if not title or not title.strip(): raise ValueError("Book title cannot be empty")
        if not author or not author.strip(): raise ValueError("Author name cannot be empty")
        if copies < 1: raise ValueError("Copies must be at least 1")
        b = self.catalog.add(title, author, copies)
        self.notifier.send(f"Book '{title}' added")
        return b

    def issue_book(self, bid, member, days=MAX_BORROW_DAYS):
        if not member or not member.strip(): raise ValueError("Member name cannot be empty")
        b = self.catalog.get(bid)
        self.lending.issue(b, member, days)
        self.notifier.send(f"Book {bid} issued to {member}")
        return b

    def return_book(self, bid, member, days_kept):
        b = self.catalog.get(bid)
        fine = self.lending.return_book(b, member, days_kept)
        self.notifier.send(f"Book {bid} returned by {member}")
        return {"book": b, "fine": fine}

    def calculate_fine(self, days_kept, allowed=MAX_BORROW_DAYS):
        return self.lending.calculate_fine(days_kept, allowed)

    def check_availability(self, bid):
        return self.catalog.get(bid)["available_copies"] > 0

    def get_book_status(self, bid):
        b = self.catalog.get(bid)
        return {
            "id": b["id"], "title": b["title"], "author": b["author"],
            "total_copies": b["total_copies"], "available_copies": b["available_copies"],
            "issued_count": len(b["issued_to"]), "status": b["status"],
        }

    def get_book(self, bid):
        return self.catalog.get(bid)

    def get_all_books(self):
        return self.catalog.get_all()
