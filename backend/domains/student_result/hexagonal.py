"""
Hexagonal Architecture — Student Result System
Ports & Adapters with domain isolation.
"""
from abc import ABC, abstractmethod

GRADE_BOUNDARIES = [
    (90, "A+"), (80, "A"), (70, "B+"), (60, "B"),
    (50, "C"), (40, "D"), (0, "F"),
]
MAX_MARKS_PER_SUBJECT = 100


# ── Domain Entity ──────────────────────────────────────────────────────
class Student:
    def __init__(self, sid: int, name: str, roll_number: str):
        self.id = sid
        self.name = name
        self.roll_number = roll_number
        self.subjects: dict[str, float] = {}
        self.total_marks = 0
        self.percentage = 0.0
        self.grade = "N/A"
        self.status = "pending"

    def add_marks(self, subject: str, marks: float):
        if marks < 0 or marks > MAX_MARKS_PER_SUBJECT:
            raise ValueError(f"Marks must be between 0 and {MAX_MARKS_PER_SUBJECT}")
        if not subject or not subject.strip():
            raise ValueError("Subject name cannot be empty")
        self.subjects[subject.strip()] = marks
        self._recalculate()

    def _recalculate(self):
        if not self.subjects:
            self.total_marks, self.percentage, self.grade, self.status = 0, 0.0, "N/A", "pending"
            return
        total = sum(self.subjects.values())
        pct = total / len(self.subjects)
        self.total_marks = round(total, 2)
        self.percentage = round(pct, 2)
        self.grade = next((g for b, g in GRADE_BOUNDARIES if pct >= b), "F")
        self.status = "pass" if pct >= 40 else "fail"

    def to_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name, "roll_number": self.roll_number,
            "subjects": self.subjects, "total_marks": self.total_marks,
            "percentage": self.percentage, "grade": self.grade, "status": self.status,
        }


# ── Port (repository) ─────────────────────────────────────────────────
class StudentRepoPort(ABC):
    @abstractmethod
    def save(self, student: Student) -> Student: ...
    @abstractmethod
    def find_by_id(self, sid: int) -> Student | None: ...
    @abstractmethod
    def find_all(self) -> list[Student]: ...


# ── Adapter (in-memory) ───────────────────────────────────────────────
class InMemoryStudentAdapter(StudentRepoPort):
    def __init__(self):
        self._store: dict[int, Student] = {}

    def save(self, student: Student) -> Student:
        self._store[student.id] = student
        return student

    def find_by_id(self, sid: int) -> Student | None:
        return self._store.get(sid)

    def find_all(self) -> list[Student]:
        return list(self._store.values())


# ── Service Adapter ────────────────────────────────────────────────────
class StudentServiceAdapter:
    def __init__(self, repo: StudentRepoPort):
        self.repo = repo
        self._next_id = 1

    def add_student(self, name: str, roll_number: str) -> dict:
        if not name or not name.strip():
            raise ValueError("Student name cannot be empty")
        if not roll_number or not roll_number.strip():
            raise ValueError("Roll number cannot be empty")
        s = Student(self._next_id, name.strip(), roll_number.strip())
        self._next_id += 1
        self.repo.save(s)
        return s.to_dict()

    def add_marks(self, sid: int, subject: str, marks: float) -> dict:
        s = self.repo.find_by_id(sid)
        if s is None: raise ValueError(f"Student {sid} not found")
        s.add_marks(subject, marks)
        self.repo.save(s)
        return s.to_dict()

    def calculate_total_marks(self, sid: int) -> float:
        s = self.repo.find_by_id(sid)
        if s is None: raise ValueError(f"Student {sid} not found")
        return s.total_marks

    def calculate_percentage(self, sid: int) -> float:
        s = self.repo.find_by_id(sid)
        if s is None: raise ValueError(f"Student {sid} not found")
        return s.percentage

    def get_grade(self, sid: int) -> str:
        s = self.repo.find_by_id(sid)
        if s is None: raise ValueError(f"Student {sid} not found")
        return s.grade

    def generate_result(self, sid: int) -> dict:
        s = self.repo.find_by_id(sid)
        if s is None: raise ValueError(f"Student {sid} not found")
        return s.to_dict()

    def get_student(self, sid: int) -> dict:
        s = self.repo.find_by_id(sid)
        if s is None: raise ValueError(f"Student {sid} not found")
        return s.to_dict()

    def get_all_students(self) -> list[dict]:
        return [s.to_dict() for s in self.repo.find_all()]


# ── Controller (wiring) ───────────────────────────────────────────────
class StudentController:
    def __init__(self):
        self._svc = StudentServiceAdapter(InMemoryStudentAdapter())

    def add_student(self, name, roll_number): return self._svc.add_student(name, roll_number)
    def add_marks(self, sid, subject, marks): return self._svc.add_marks(sid, subject, marks)
    def calculate_total_marks(self, sid): return self._svc.calculate_total_marks(sid)
    def calculate_percentage(self, sid): return self._svc.calculate_percentage(sid)
    def get_grade(self, sid): return self._svc.get_grade(sid)
    def generate_result(self, sid): return self._svc.generate_result(sid)
    def get_student(self, sid): return self._svc.get_student(sid)
    def get_all_students(self): return self._svc.get_all_students()
