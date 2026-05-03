"""
MVC Architecture — Library Management System
"""

FINE_PER_DAY = 2.0
MAX_BORROW_DAYS = 14


# ── Model ──────────────────────────────────────────────────────────────
class BookModel:
    _store: dict = {}
    _next_id: int = 1

    @classmethod
    def reset(cls):
        cls._store = {}
        cls._next_id = 1

    @classmethod
    def create(cls, title: str, author: str, copies: int) -> dict:
        book = {
            "id": cls._next_id, "title": title.strip(), "author": author.strip(),
            "total_copies": copies, "available_copies": copies,
            "issued_to": [], "status": "available",
        }
        cls._store[cls._next_id] = book
        cls._next_id += 1
        return book

    @classmethod
    def get(cls, bid: int) -> dict | None:
        return cls._store.get(bid)

    @classmethod
    def get_all(cls) -> list[dict]:
        return list(cls._store.values())


# ── View ───────────────────────────────────────────────────────────────
class BookView:
    @staticmethod
    def render(book: dict) -> dict:
        return book

    @staticmethod
    def render_status(book: dict) -> dict:
        return {
            "id": book["id"], "title": book["title"], "author": book["author"],
            "total_copies": book["total_copies"],
            "available_copies": book["available_copies"],
            "issued_count": len(book["issued_to"]),
            "status": book["status"],
        }


# ── Controller ─────────────────────────────────────────────────────────
class LibraryController:
    def __init__(self):
        BookModel.reset()
        self.view = BookView()

    def add_book(self, title: str, author: str, copies: int = 1) -> dict:
        if not title or not title.strip(): raise ValueError("Book title cannot be empty")
        if not author or not author.strip(): raise ValueError("Author name cannot be empty")
        if copies < 1: raise ValueError("Copies must be at least 1")
        return self.view.render(BookModel.create(title, author, copies))

    def issue_book(self, bid: int, member: str, days: int = MAX_BORROW_DAYS) -> dict:
        book = BookModel.get(bid)
        if book is None: raise ValueError(f"Book {bid} not found")
        if book["available_copies"] <= 0: raise ValueError("No copies available")
        if not member or not member.strip(): raise ValueError("Member name cannot be empty")
        book["available_copies"] -= 1
        book["issued_to"].append({"member": member.strip(), "days": days})
        book["status"] = "available" if book["available_copies"] > 0 else "all_issued"
        return self.view.render(book)

    def return_book(self, bid: int, member: str, days_kept: int) -> dict:
        book = BookModel.get(bid)
        if book is None: raise ValueError(f"Book {bid} not found")
        rec = next((r for r in book["issued_to"] if r["member"] == member.strip()), None)
        if rec is None: raise ValueError(f"No issue record for member '{member}'")
        book["issued_to"].remove(rec)
        book["available_copies"] += 1
        book["status"] = "available"
        fine = self.calculate_fine(days_kept, rec.get("days", MAX_BORROW_DAYS))
        return {"book": self.view.render(book), "fine": fine}

    @staticmethod
    def calculate_fine(days_kept: int, allowed: int = MAX_BORROW_DAYS) -> float:
        if days_kept <= allowed: return 0.0
        return round((days_kept - allowed) * FINE_PER_DAY, 2)

    def check_availability(self, bid: int) -> bool:
        book = BookModel.get(bid)
        if book is None: raise ValueError(f"Book {bid} not found")
        return book["available_copies"] > 0

    def get_book_status(self, bid: int) -> dict:
        book = BookModel.get(bid)
        if book is None: raise ValueError(f"Book {bid} not found")
        return self.view.render_status(book)

    def get_book(self, bid: int) -> dict:
        book = BookModel.get(bid)
        if book is None: raise ValueError(f"Book {bid} not found")
        return self.view.render(book)

    def get_all_books(self) -> list[dict]:
        return [self.view.render(b) for b in BookModel.get_all()]
