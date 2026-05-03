"""
MVC Architecture — Student Result System
Model-View-Controller separation.
"""

GRADE_BOUNDARIES = [
    (90, "A+"), (80, "A"), (70, "B+"), (60, "B"),
    (50, "C"), (40, "D"), (0, "F"),
]
MAX_MARKS_PER_SUBJECT = 100


# ── Model ──────────────────────────────────────────────────────────────
class StudentModel:
    _store: dict = {}
    _next_id: int = 1

    @classmethod
    def reset(cls):
        cls._store = {}
        cls._next_id = 1

    @classmethod
    def create(cls, name: str, roll_number: str) -> dict:
        student = {
            "id": cls._next_id, "name": name.strip(),
            "roll_number": roll_number.strip(), "subjects": {},
            "total_marks": 0, "percentage": 0.0,
            "grade": "N/A", "status": "pending",
        }
        cls._store[cls._next_id] = student
        cls._next_id += 1
        return student

    @classmethod
    def get(cls, sid: int) -> dict | None:
        return cls._store.get(sid)

    @classmethod
    def get_all(cls) -> list[dict]:
        return list(cls._store.values())

    @classmethod
    def add_marks(cls, sid: int, subject: str, marks: float) -> dict:
        student = cls.get(sid)
        if student is None:
            raise ValueError(f"Student {sid} not found")
        if marks < 0 or marks > MAX_MARKS_PER_SUBJECT:
            raise ValueError(f"Marks must be between 0 and {MAX_MARKS_PER_SUBJECT}")
        if not subject or not subject.strip():
            raise ValueError("Subject name cannot be empty")
        student["subjects"][subject.strip()] = marks
        cls._recalculate(student)
        return student

    @classmethod
    def _recalculate(cls, student: dict):
        subs = student["subjects"]
        if not subs:
            student.update({"total_marks": 0, "percentage": 0.0, "grade": "N/A", "status": "pending"})
            return
        total = sum(subs.values())
        pct = total / len(subs)
        grade = next((g for b, g in GRADE_BOUNDARIES if pct >= b), "F")
        student.update({
            "total_marks": round(total, 2), "percentage": round(pct, 2),
            "grade": grade, "status": "pass" if pct >= 40 else "fail",
        })


# ── View ───────────────────────────────────────────────────────────────
class StudentView:
    @staticmethod
    def render(student: dict) -> dict:
        return student

    @staticmethod
    def render_result(student: dict) -> dict:
        return {
            "id": student["id"], "name": student["name"],
            "roll_number": student["roll_number"],
            "subjects": student["subjects"],
            "total_marks": student["total_marks"],
            "percentage": student["percentage"],
            "grade": student["grade"], "status": student["status"],
        }


# ── Controller ─────────────────────────────────────────────────────────
class StudentController:
    def __init__(self):
        StudentModel.reset()
        self.view = StudentView()

    def add_student(self, name: str, roll_number: str) -> dict:
        if not name or not name.strip():
            raise ValueError("Student name cannot be empty")
        if not roll_number or not roll_number.strip():
            raise ValueError("Roll number cannot be empty")
        return self.view.render(StudentModel.create(name, roll_number))

    def add_marks(self, sid: int, subject: str, marks: float) -> dict:
        return self.view.render(StudentModel.add_marks(sid, subject, marks))

    def calculate_total_marks(self, sid: int) -> float:
        s = StudentModel.get(sid)
        if s is None: raise ValueError(f"Student {sid} not found")
        return s["total_marks"]

    def calculate_percentage(self, sid: int) -> float:
        s = StudentModel.get(sid)
        if s is None: raise ValueError(f"Student {sid} not found")
        return s["percentage"]

    def get_grade(self, sid: int) -> str:
        s = StudentModel.get(sid)
        if s is None: raise ValueError(f"Student {sid} not found")
        return s["grade"]

    def generate_result(self, sid: int) -> dict:
        s = StudentModel.get(sid)
        if s is None: raise ValueError(f"Student {sid} not found")
        return self.view.render_result(s)

    def get_student(self, sid: int) -> dict:
        s = StudentModel.get(sid)
        if s is None: raise ValueError(f"Student {sid} not found")
        return self.view.render(s)

    def get_all_students(self) -> list[dict]:
        return [self.view.render(s) for s in StudentModel.get_all()]
