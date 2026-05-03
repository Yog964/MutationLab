"""
Microservices Architecture — Student Result System
Independent services coordinated by an API Gateway.
"""

GRADE_BOUNDARIES = [
    (90, "A+"), (80, "A"), (70, "B+"), (60, "B"),
    (50, "C"), (40, "D"), (0, "F"),
]
MAX_MARKS_PER_SUBJECT = 100


# ── Student Service ────────────────────────────────────────────────────
class StudentService:
    def __init__(self):
        self._students: dict[int, dict] = {}
        self._next_id = 1

    def create(self, name: str, roll_number: str) -> dict:
        s = {
            "id": self._next_id, "name": name.strip(),
            "roll_number": roll_number.strip(), "subjects": {},
            "total_marks": 0, "percentage": 0.0,
            "grade": "N/A", "status": "pending",
        }
        self._students[self._next_id] = s
        self._next_id += 1
        return s

    def get(self, sid: int) -> dict:
        s = self._students.get(sid)
        if s is None: raise ValueError(f"Student {sid} not found")
        return s

    def get_all(self) -> list[dict]:
        return list(self._students.values())


# ── Grading Service ────────────────────────────────────────────────────
class GradingService:
    def calculate(self, subjects: dict) -> dict:
        if not subjects:
            return {"total": 0, "percentage": 0.0, "grade": "N/A", "status": "pending"}
        total = sum(subjects.values())
        pct = total / len(subjects)
        grade = next((g for b, g in GRADE_BOUNDARIES if pct >= b), "F")
        return {
            "total": round(total, 2), "percentage": round(pct, 2),
            "grade": grade, "status": "pass" if pct >= 40 else "fail",
        }


# ── Validation Service ─────────────────────────────────────────────────
class ValidationService:
    def validate_marks(self, marks: float) -> bool:
        if marks < 0 or marks > MAX_MARKS_PER_SUBJECT:
            raise ValueError(f"Marks must be between 0 and {MAX_MARKS_PER_SUBJECT}")
        return True

    def validate_subject(self, subject: str) -> bool:
        if not subject or not subject.strip():
            raise ValueError("Subject name cannot be empty")
        return True


# ── Notification Service ───────────────────────────────────────────────
class NotificationService:
    def __init__(self):
        self.log: list[str] = []

    def send(self, msg: str):
        self.log.append(msg)


# ── Gateway / Controller ──────────────────────────────────────────────
class StudentController:
    def __init__(self):
        self.student_svc = StudentService()
        self.grading_svc = GradingService()
        self.validation_svc = ValidationService()
        self.notification_svc = NotificationService()

    def add_student(self, name: str, roll_number: str) -> dict:
        if not name or not name.strip():
            raise ValueError("Student name cannot be empty")
        if not roll_number or not roll_number.strip():
            raise ValueError("Roll number cannot be empty")
        s = self.student_svc.create(name, roll_number)
        self.notification_svc.send(f"Student {s['id']} created")
        return s

    def add_marks(self, sid: int, subject: str, marks: float) -> dict:
        self.validation_svc.validate_subject(subject)
        self.validation_svc.validate_marks(marks)
        s = self.student_svc.get(sid)
        s["subjects"][subject.strip()] = marks
        result = self.grading_svc.calculate(s["subjects"])
        s.update({"total_marks": result["total"], "percentage": result["percentage"],
                  "grade": result["grade"], "status": result["status"]})
        return s

    def calculate_total_marks(self, sid: int) -> float:
        return self.student_svc.get(sid)["total_marks"]

    def calculate_percentage(self, sid: int) -> float:
        return self.student_svc.get(sid)["percentage"]

    def get_grade(self, sid: int) -> str:
        return self.student_svc.get(sid)["grade"]

    def generate_result(self, sid: int) -> dict:
        s = self.student_svc.get(sid)
        return {
            "id": s["id"], "name": s["name"], "roll_number": s["roll_number"],
            "subjects": s["subjects"], "total_marks": s["total_marks"],
            "percentage": s["percentage"], "grade": s["grade"], "status": s["status"],
        }

    def get_student(self, sid: int) -> dict:
        return self.student_svc.get(sid)

    def get_all_students(self) -> list[dict]:
        return self.student_svc.get_all()
