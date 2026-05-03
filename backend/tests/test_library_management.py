"""
Unified test suite for Library Management System — runs same tests against all 5 architectures.
"""
import pytest

from domains.library_management.layered import LibraryController as LayeredCtrl
from domains.library_management.mvc import LibraryController as MvcCtrl
from domains.library_management.hexagonal import LibraryController as HexCtrl
from domains.library_management.microservices import LibraryController as MicroCtrl
from domains.library_management.event_driven import LibraryController as EventCtrl


@pytest.fixture(params=[LayeredCtrl, MvcCtrl, HexCtrl, MicroCtrl, EventCtrl],
                ids=["layered", "mvc", "hexagonal", "microservices", "event_driven"])
def ctrl(request):
    return request.param()


class TestBookManagement:
    def test_add_book(self, ctrl):
        b = ctrl.add_book("Python 101", "Author A", 3)
        assert b["title"] == "Python 101"
        assert b["available_copies"] == 3

    def test_empty_title_rejected(self, ctrl):
        with pytest.raises(ValueError, match="empty"):
            ctrl.add_book("", "Author", 1)

    def test_empty_author_rejected(self, ctrl):
        with pytest.raises(ValueError, match="empty"):
            ctrl.add_book("Title", "", 1)

    def test_zero_copies_rejected(self, ctrl):
        with pytest.raises(ValueError):
            ctrl.add_book("Title", "Author", 0)


class TestIssueReturn:
    def test_issue_book(self, ctrl):
        b = ctrl.add_book("Book", "Author", 2)
        b = ctrl.issue_book(b["id"], "Alice")
        assert b["available_copies"] == 1

    def test_issue_all_copies(self, ctrl):
        b = ctrl.add_book("Book", "Author", 1)
        b = ctrl.issue_book(b["id"], "Alice")
        assert b["available_copies"] == 0
        assert b["status"] == "all_issued"

    def test_issue_no_copies(self, ctrl):
        b = ctrl.add_book("Book", "Author", 1)
        ctrl.issue_book(b["id"], "Alice")
        with pytest.raises(ValueError, match="No copies"):
            ctrl.issue_book(b["id"], "Bob")

    def test_issue_empty_member(self, ctrl):
        b = ctrl.add_book("Book", "Author", 1)
        with pytest.raises(ValueError, match="empty"):
            ctrl.issue_book(b["id"], "")

    def test_return_book_no_fine(self, ctrl):
        b = ctrl.add_book("Book", "Author", 1)
        ctrl.issue_book(b["id"], "Alice")
        result = ctrl.return_book(b["id"], "Alice", 10)
        assert result["fine"] == 0.0
        assert result["book"]["available_copies"] == 1

    def test_return_book_with_fine(self, ctrl):
        b = ctrl.add_book("Book", "Author", 1)
        ctrl.issue_book(b["id"], "Alice")
        result = ctrl.return_book(b["id"], "Alice", 20)  # 6 days overdue
        assert result["fine"] == 12.0  # 6 * 2.0

    def test_return_wrong_member(self, ctrl):
        b = ctrl.add_book("Book", "Author", 1)
        ctrl.issue_book(b["id"], "Alice")
        with pytest.raises(ValueError, match="No issue record"):
            ctrl.return_book(b["id"], "Bob", 5)


class TestFineCalculation:
    def test_no_fine(self, ctrl):
        assert ctrl.calculate_fine(10) == 0.0

    def test_fine_overdue(self, ctrl):
        assert ctrl.calculate_fine(17) == 6.0  # 3 days * 2.0

    def test_fine_exact_limit(self, ctrl):
        assert ctrl.calculate_fine(14) == 0.0


class TestQueries:
    def test_check_availability(self, ctrl):
        b = ctrl.add_book("Book", "Author", 1)
        assert ctrl.check_availability(b["id"]) is True
        ctrl.issue_book(b["id"], "Alice")
        assert ctrl.check_availability(b["id"]) is False

    def test_get_book_status(self, ctrl):
        b = ctrl.add_book("Book", "Author", 2)
        ctrl.issue_book(b["id"], "Alice")
        status = ctrl.get_book_status(b["id"])
        assert status["issued_count"] == 1
        assert status["available_copies"] == 1

    def test_get_nonexistent(self, ctrl):
        with pytest.raises(ValueError, match="not found"):
            ctrl.get_book(999)

    def test_get_all_books(self, ctrl):
        ctrl.add_book("A", "Author", 1)
        ctrl.add_book("B", "Author", 1)
        assert len(ctrl.get_all_books()) == 2
