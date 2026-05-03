"""
Layered Architecture — Student Result System
Layers: Presentation → Business Logic → Data Access
"""

# ── Data Access Layer ──────────────────────────────────────────────────
class StudentRepository:
    """Stores student records and their marks."""

    def __init__(self):
        self._students: dict[int, dict] = {}
        self._next_id = 1

    def save(self, student: dict) -> dict:
        sid = self._next_id
        self._next_id += 1
        student["id"] = sid
        self._students[sid] = student
        return student

    def find_by_id(self, sid: int) -> dict | None:
        return self._students.get(sid)

    def find_all(self) -> list[dict]:
        return list(self._students.values())

    def update(self, sid: int, data: dict) -> dict | None:
        if sid in self._students:
            self._students[sid] = data
            return data
        return None

    def delete(self, sid: int) -> bool:
        return self._students.pop(sid, None) is not None


# ── Business Logic Layer ───────────────────────────────────────────────
GRADE_BOUNDARIES = [
    (90, "A+"), (80, "A"), (70, "B+"), (60, "B"),
    (50, "C"), (40, "D"), (0, "F"),
]
MAX_MARKS_PER_SUBJECT = 100


class StudentService:
    """Business rules for student result processing."""

    def __init__(self, repo: StudentRepository):
        self.repo = repo

    def add_student(self, name: str, roll_number: str) -> dict:
        if not name or not name.strip():
            raise ValueError("Student name cannot be empty")
        if not roll_number or not roll_number.strip():
            raise ValueError("Roll number cannot be empty")
        student = {
            "name": name.strip(),
            "roll_number": roll_number.strip(),
            "subjects": {},
            "total_marks": 0,
            "percentage": 0.0,
            "grade": "N/A",
            "status": "pending",
        }
        return self.repo.save(student)

    def add_marks(self, sid: int, subject: str, marks: float) -> dict:
        student = self.repo.find_by_id(sid)
        if student is None:
            raise ValueError(f"Student {sid} not found")
        if marks < 0 or marks > MAX_MARKS_PER_SUBJECT:
            raise ValueError(f"Marks must be between 0 and {MAX_MARKS_PER_SUBJECT}")
        if not subject or not subject.strip():
            raise ValueError("Subject name cannot be empty")
        student["subjects"][subject.strip()] = marks
        self._recalculate(student)
        self.repo.update(sid, student)
        return student

    def _recalculate(self, student: dict):
        subjects = student["subjects"]
        if not subjects:
            student["total_marks"] = 0
            student["percentage"] = 0.0
            student["grade"] = "N/A"
            student["status"] = "pending"
            return
        total = sum(subjects.values())
        percentage = total / len(subjects)
        student["total_marks"] = round(total, 2)
        student["percentage"] = round(percentage, 2)
        student["grade"] = self._assign_grade(percentage)
        student["status"] = "pass" if percentage >= 40 else "fail"

    @staticmethod
    def _assign_grade(percentage: float) -> str:
        for boundary, grade in GRADE_BOUNDARIES:
            if percentage >= boundary:
                return grade
        return "F"

    def calculate_total_marks(self, sid: int) -> float:
        student = self.repo.find_by_id(sid)
        if student is None:
            raise ValueError(f"Student {sid} not found")
        return student["total_marks"]

    def calculate_percentage(self, sid: int) -> float:
        student = self.repo.find_by_id(sid)
        if student is None:
            raise ValueError(f"Student {sid} not found")
        return student["percentage"]

    def get_grade(self, sid: int) -> str:
        student = self.repo.find_by_id(sid)
        if student is None:
            raise ValueError(f"Student {sid} not found")
        return student["grade"]

    def generate_result(self, sid: int) -> dict:
        student = self.repo.find_by_id(sid)
        if student is None:
            raise ValueError(f"Student {sid} not found")
        return {
            "id": student["id"],
            "name": student["name"],
            "roll_number": student["roll_number"],
            "subjects": student["subjects"],
            "total_marks": student["total_marks"],
            "percentage": student["percentage"],
            "grade": student["grade"],
            "status": student["status"],
        }

    def get_student(self, sid: int) -> dict:
        student = self.repo.find_by_id(sid)
        if student is None:
            raise ValueError(f"Student {sid} not found")
        return student

    def get_all_students(self) -> list[dict]:
        return self.repo.find_all()


# ── Presentation Layer ─────────────────────────────────────────────────
class StudentController:
    """Thin controller that delegates to the service."""

    def __init__(self):
        self.service = StudentService(StudentRepository())

    def add_student(self, name: str, roll_number: str) -> dict:
        return self.service.add_student(name, roll_number)

    def add_marks(self, sid: int, subject: str, marks: float) -> dict:
        return self.service.add_marks(sid, subject, marks)

    def calculate_total_marks(self, sid: int) -> float:
        return self.service.calculate_total_marks(sid)

    def calculate_percentage(self, sid: int) -> float:
        return self.service.calculate_percentage(sid)

    def get_grade(self, sid: int) -> str:
        return self.service.get_grade(sid)

    def generate_result(self, sid: int) -> dict:
        return self.service.generate_result(sid)

    def get_student(self, sid: int) -> dict:
        return self.service.get_student(sid)

    def get_all_students(self) -> list[dict]:
        return self.service.get_all_students()
