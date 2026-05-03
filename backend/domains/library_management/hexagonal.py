"""
Hexagonal Architecture — Library Management System
Ports & Adapters with domain isolation.
"""
from abc import ABC, abstractmethod

FINE_PER_DAY = 2.0
MAX_BORROW_DAYS = 14


# ── Domain Entity ──────────────────────────────────────────────────────
class Book:
    def __init__(self, bid: int, title: str, author: str, copies: int = 1):
        self.id = bid
        self.title = title
        self.author = author
        self.total_copies = copies
        self.available_copies = copies
        self.issued_to: list[dict] = []
        self.status = "available"

    def issue(self, member: str, days: int = MAX_BORROW_DAYS):
        if self.available_copies <= 0: raise ValueError("No copies available")
        if not member or not member.strip(): raise ValueError("Member name cannot be empty")
        self.available_copies -= 1
        self.issued_to.append({"member": member.strip(), "days": days})
        self.status = "available" if self.available_copies > 0 else "all_issued"

    def return_book(self, member: str, days_kept: int) -> float:
        rec = next((r for r in self.issued_to if r["member"] == member.strip()), None)
        if rec is None: raise ValueError(f"No issue record for member '{member}'")
        self.issued_to.remove(rec)
        self.available_copies += 1
        self.status = "available"
        return self._calculate_fine(days_kept, rec.get("days", MAX_BORROW_DAYS))

    @staticmethod
    def _calculate_fine(days_kept: int, allowed: int) -> float:
        if days_kept <= allowed: return 0.0
        return round((days_kept - allowed) * FINE_PER_DAY, 2)

    def to_dict(self) -> dict:
        return {
            "id": self.id, "title": self.title, "author": self.author,
            "total_copies": self.total_copies, "available_copies": self.available_copies,
            "issued_to": self.issued_to, "status": self.status,
        }

    def status_dict(self) -> dict:
        return {
            "id": self.id, "title": self.title, "author": self.author,
            "total_copies": self.total_copies, "available_copies": self.available_copies,
            "issued_count": len(self.issued_to), "status": self.status,
        }


# ── Port ───────────────────────────────────────────────────────────────
class BookRepoPort(ABC):
    @abstractmethod
    def save(self, book: Book) -> Book: ...
    @abstractmethod
    def find_by_id(self, bid: int) -> Book | None: ...
    @abstractmethod
    def find_all(self) -> list[Book]: ...


# ── Adapter ────────────────────────────────────────────────────────────
class InMemoryBookAdapter(BookRepoPort):
    def __init__(self): self._store: dict[int, Book] = {}
    def save(self, book): self._store[book.id] = book; return book
    def find_by_id(self, bid): return self._store.get(bid)
    def find_all(self): return list(self._store.values())


class LibraryServiceAdapter:
    def __init__(self, repo: BookRepoPort):
        self.repo = repo
        self._next_id = 1

    def add_book(self, title, author, copies=1):
        if not title or not title.strip(): raise ValueError("Book title cannot be empty")
        if not author or not author.strip(): raise ValueError("Author name cannot be empty")
        if copies < 1: raise ValueError("Copies must be at least 1")
        b = Book(self._next_id, title.strip(), author.strip(), copies)
        self._next_id += 1
        self.repo.save(b)
        return b.to_dict()

    def issue_book(self, bid, member, days=MAX_BORROW_DAYS):
        b = self.repo.find_by_id(bid)
        if b is None: raise ValueError(f"Book {bid} not found")
        b.issue(member, days)
        self.repo.save(b)
        return b.to_dict()

    def return_book(self, bid, member, days_kept):
        b = self.repo.find_by_id(bid)
        if b is None: raise ValueError(f"Book {bid} not found")
        fine = b.return_book(member, days_kept)
        self.repo.save(b)
        return {"book": b.to_dict(), "fine": fine}

    @staticmethod
    def calculate_fine(days_kept, allowed=MAX_BORROW_DAYS):
        if days_kept <= allowed: return 0.0
        return round((days_kept - allowed) * FINE_PER_DAY, 2)

    def check_availability(self, bid):
        b = self.repo.find_by_id(bid)
        if b is None: raise ValueError(f"Book {bid} not found")
        return b.available_copies > 0

    def get_book_status(self, bid):
        b = self.repo.find_by_id(bid)
        if b is None: raise ValueError(f"Book {bid} not found")
        return b.status_dict()

    def get_book(self, bid):
        b = self.repo.find_by_id(bid)
        if b is None: raise ValueError(f"Book {bid} not found")
        return b.to_dict()

    def get_all_books(self):
        return [b.to_dict() for b in self.repo.find_all()]


# ── Controller ─────────────────────────────────────────────────────────
class LibraryController:
    def __init__(self):
        self._svc = LibraryServiceAdapter(InMemoryBookAdapter())

    def add_book(self, title, author, copies=1): return self._svc.add_book(title, author, copies)
    def issue_book(self, bid, member, days=MAX_BORROW_DAYS): return self._svc.issue_book(bid, member, days)
    def return_book(self, bid, member, days_kept): return self._svc.return_book(bid, member, days_kept)
    def calculate_fine(self, days_kept, allowed=MAX_BORROW_DAYS): return self._svc.calculate_fine(days_kept, allowed)
    def check_availability(self, bid): return self._svc.check_availability(bid)
    def get_book_status(self, bid): return self._svc.get_book_status(bid)
    def get_book(self, bid): return self._svc.get_book(bid)
    def get_all_books(self): return self._svc.get_all_books()
