"""
Unified test suite for Student Result System — runs same tests against all 5 architectures.
"""
import pytest

from domains.student_result.layered import StudentController as LayeredCtrl
from domains.student_result.mvc import StudentController as MvcCtrl
from domains.student_result.hexagonal import StudentController as HexCtrl
from domains.student_result.microservices import StudentController as MicroCtrl
from domains.student_result.event_driven import StudentController as EventCtrl


@pytest.fixture(params=[LayeredCtrl, MvcCtrl, HexCtrl, MicroCtrl, EventCtrl],
                ids=["layered", "mvc", "hexagonal", "microservices", "event_driven"])
def ctrl(request):
    return request.param()


class TestStudentCreation:
    def test_add_student(self, ctrl):
        s = ctrl.add_student("Alice", "R001")
        assert s["name"] == "Alice"
        assert s["roll_number"] == "R001"
        assert s["status"] == "pending"

    def test_empty_name_rejected(self, ctrl):
        with pytest.raises(ValueError, match="empty"):
            ctrl.add_student("", "R001")

    def test_empty_roll_rejected(self, ctrl):
        with pytest.raises(ValueError, match="empty"):
            ctrl.add_student("Alice", "")


class TestMarks:
    def test_add_marks(self, ctrl):
        s = ctrl.add_student("Alice", "R001")
        s = ctrl.add_marks(s["id"], "Math", 85)
        assert s["subjects"]["Math"] == 85

    def test_negative_marks_rejected(self, ctrl):
        s = ctrl.add_student("Alice", "R001")
        with pytest.raises(ValueError):
            ctrl.add_marks(s["id"], "Math", -5)

    def test_excess_marks_rejected(self, ctrl):
        s = ctrl.add_student("Alice", "R001")
        with pytest.raises(ValueError):
            ctrl.add_marks(s["id"], "Math", 150)

    def test_empty_subject_rejected(self, ctrl):
        s = ctrl.add_student("Alice", "R001")
        with pytest.raises(ValueError, match="empty"):
            ctrl.add_marks(s["id"], "", 50)

    def test_marks_to_nonexistent(self, ctrl):
        with pytest.raises(ValueError, match="not found"):
            ctrl.add_marks(999, "Math", 50)


class TestCalculations:
    def test_total_marks(self, ctrl):
        s = ctrl.add_student("Alice", "R001")
        ctrl.add_marks(s["id"], "Math", 80)
        ctrl.add_marks(s["id"], "Science", 70)
        assert ctrl.calculate_total_marks(s["id"]) == 150

    def test_percentage(self, ctrl):
        s = ctrl.add_student("Alice", "R001")
        ctrl.add_marks(s["id"], "Math", 80)
        ctrl.add_marks(s["id"], "Science", 70)
        assert ctrl.calculate_percentage(s["id"]) == 75.0

    def test_grade_a_plus(self, ctrl):
        s = ctrl.add_student("Alice", "R001")
        ctrl.add_marks(s["id"], "Math", 95)
        assert ctrl.get_grade(s["id"]) == "A+"

    def test_grade_f_fail(self, ctrl):
        s = ctrl.add_student("Alice", "R001")
        ctrl.add_marks(s["id"], "Math", 30)
        assert ctrl.get_grade(s["id"]) == "F"
        r = ctrl.generate_result(s["id"])
        assert r["status"] == "fail"

    def test_pass_status(self, ctrl):
        s = ctrl.add_student("Alice", "R001")
        ctrl.add_marks(s["id"], "Math", 60)
        r = ctrl.generate_result(s["id"])
        assert r["status"] == "pass"


class TestQueries:
    def test_get_student(self, ctrl):
        s = ctrl.add_student("Alice", "R001")
        assert ctrl.get_student(s["id"])["name"] == "Alice"

    def test_get_nonexistent(self, ctrl):
        with pytest.raises(ValueError, match="not found"):
            ctrl.get_student(999)

    def test_get_all(self, ctrl):
        ctrl.add_student("Alice", "R001")
        ctrl.add_student("Bob", "R002")
        assert len(ctrl.get_all_students()) == 2

    def test_generate_result(self, ctrl):
        s = ctrl.add_student("Alice", "R001")
        ctrl.add_marks(s["id"], "Math", 85)
        r = ctrl.generate_result(s["id"])
        assert "grade" in r
        assert "percentage" in r
