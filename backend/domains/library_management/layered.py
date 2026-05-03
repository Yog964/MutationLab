"""
Layered Architecture — Library Management System
Layers: Presentation → Business Logic → Data Access
"""

FINE_PER_DAY = 2.0
MAX_BORROW_DAYS = 14


# ── Data Access Layer ──────────────────────────────────────────────────
class BookRepository:
    def __init__(self):
        self._books: dict[int, dict] = {}
        self._next_id = 1

    def save(self, book: dict) -> dict:
        bid = self._next_id
        self._next_id += 1
        book["id"] = bid
        self._books[bid] = book
        return book

    def find_by_id(self, bid: int) -> dict | None:
        return self._books.get(bid)

    def find_all(self) -> list[dict]:
        return list(self._books.values())

    def update(self, bid: int, data: dict) -> dict | None:
        if bid in self._books:
            self._books[bid] = data
            return data
        return None


# ── Business Logic Layer ───────────────────────────────────────────────
class LibraryService:
    def __init__(self, repo: BookRepository):
        self.repo = repo

    def add_book(self, title: str, author: str, copies: int = 1) -> dict:
        if not title or not title.strip():
            raise ValueError("Book title cannot be empty")
        if not author or not author.strip():
            raise ValueError("Author name cannot be empty")
        if copies < 1:
            raise ValueError("Copies must be at least 1")
        book = {
            "title": title.strip(), "author": author.strip(),
            "total_copies": copies, "available_copies": copies,
            "issued_to": [], "status": "available",
        }
        return self.repo.save(book)

    def issue_book(self, bid: int, member: str, days: int = MAX_BORROW_DAYS) -> dict:
        book = self.repo.find_by_id(bid)
        if book is None:
            raise ValueError(f"Book {bid} not found")
        if book["available_copies"] <= 0:
            raise ValueError("No copies available")
        if not member or not member.strip():
            raise ValueError("Member name cannot be empty")
        book["available_copies"] -= 1
        book["issued_to"].append({"member": member.strip(), "days": days})
        book["status"] = "available" if book["available_copies"] > 0 else "all_issued"
        self.repo.update(bid, book)
        return book

    def return_book(self, bid: int, member: str, days_kept: int) -> dict:
        book = self.repo.find_by_id(bid)
        if book is None:
            raise ValueError(f"Book {bid} not found")
        issue_record = None
        for rec in book["issued_to"]:
            if rec["member"] == member.strip():
                issue_record = rec
                break
        if issue_record is None:
            raise ValueError(f"No issue record for member '{member}'")
        book["issued_to"].remove(issue_record)
        book["available_copies"] += 1
        book["status"] = "available"
        fine = self.calculate_fine(days_kept, issue_record.get("days", MAX_BORROW_DAYS))
        self.repo.update(bid, book)
        return {"book": book, "fine": fine}

    @staticmethod
    def calculate_fine(days_kept: int, allowed_days: int = MAX_BORROW_DAYS) -> float:
        if days_kept <= allowed_days:
            return 0.0
        overdue = days_kept - allowed_days
        return round(overdue * FINE_PER_DAY, 2)

    def check_availability(self, bid: int) -> bool:
        book = self.repo.find_by_id(bid)
        if book is None:
            raise ValueError(f"Book {bid} not found")
        return book["available_copies"] > 0

    def get_book_status(self, bid: int) -> dict:
        book = self.repo.find_by_id(bid)
        if book is None:
            raise ValueError(f"Book {bid} not found")
        return {
            "id": book["id"], "title": book["title"], "author": book["author"],
            "total_copies": book["total_copies"],
            "available_copies": book["available_copies"],
            "issued_count": len(book["issued_to"]),
            "status": book["status"],
        }

    def get_book(self, bid: int) -> dict:
        book = self.repo.find_by_id(bid)
        if book is None:
            raise ValueError(f"Book {bid} not found")
        return book

    def get_all_books(self) -> list[dict]:
        return self.repo.find_all()


# ── Presentation Layer ─────────────────────────────────────────────────
class LibraryController:
    def __init__(self):
        self.service = LibraryService(BookRepository())

    def add_book(self, title, author, copies=1): return self.service.add_book(title, author, copies)
    def issue_book(self, bid, member, days=MAX_BORROW_DAYS): return self.service.issue_book(bid, member, days)
    def return_book(self, bid, member, days_kept): return self.service.return_book(bid, member, days_kept)
    def calculate_fine(self, days_kept, allowed=MAX_BORROW_DAYS): return self.service.calculate_fine(days_kept, allowed)
    def check_availability(self, bid): return self.service.check_availability(bid)
    def get_book_status(self, bid): return self.service.get_book_status(bid)
    def get_book(self, bid): return self.service.get_book(bid)
    def get_all_books(self): return self.service.get_all_books()
