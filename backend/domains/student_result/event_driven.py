"""
Event-Driven Architecture — Student Result System
In-memory event bus with publish/subscribe pattern.
"""

GRADE_BOUNDARIES = [
    (90, "A+"), (80, "A"), (70, "B+"), (60, "B"),
    (50, "C"), (40, "D"), (0, "F"),
]
MAX_MARKS_PER_SUBJECT = 100


# ── Event Bus ──────────────────────────────────────────────────────────
class EventBus:
    def __init__(self):
        self._handlers: dict[str, list] = {}
        self.event_log: list[dict] = []

    def subscribe(self, event_type: str, handler):
        self._handlers.setdefault(event_type, []).append(handler)

    def publish(self, event_type: str, data: dict):
        self.event_log.append({"type": event_type, "data": data})
        for h in self._handlers.get(event_type, []):
            h(data)


# ── Store ──────────────────────────────────────────────────────────────
class StudentStore:
    def __init__(self):
        self._students: dict[int, dict] = {}
        self._next_id = 1

    def next_id(self) -> int:
        sid = self._next_id
        self._next_id += 1
        return sid

    def save(self, student: dict):
        self._students[student["id"]] = student

    def get(self, sid: int) -> dict | None:
        return self._students.get(sid)

    def get_all(self) -> list[dict]:
        return list(self._students.values())


# ── Event Handlers ─────────────────────────────────────────────────────
class StudentEventHandlers:
    def __init__(self, store: StudentStore, bus: EventBus):
        self.store = store
        self.bus = bus
        bus.subscribe("StudentCreated", self.on_created)
        bus.subscribe("MarksAdded", self.on_marks_added)

    def on_created(self, data: dict):
        self.store.save(data["student"])

    def on_marks_added(self, data: dict):
        s = self.store.get(data["sid"])
        if s is None:
            return
        s["subjects"] = data["subjects"]
        self._recalculate(s)
        self.store.save(s)

    @staticmethod
    def _recalculate(s: dict):
        subs = s["subjects"]
        if not subs:
            s.update({"total_marks": 0, "percentage": 0.0, "grade": "N/A", "status": "pending"})
            return
        total = sum(subs.values())
        pct = total / len(subs)
        grade = next((g for b, g in GRADE_BOUNDARIES if pct >= b), "F")
        s.update({
            "total_marks": round(total, 2), "percentage": round(pct, 2),
            "grade": grade, "status": "pass" if pct >= 40 else "fail",
        })


# ── Controller ─────────────────────────────────────────────────────────
class StudentController:
    def __init__(self):
        self.bus = EventBus()
        self.store = StudentStore()
        self.handlers = StudentEventHandlers(self.store, self.bus)

    def add_student(self, name: str, roll_number: str) -> dict:
        if not name or not name.strip():
            raise ValueError("Student name cannot be empty")
        if not roll_number or not roll_number.strip():
            raise ValueError("Roll number cannot be empty")
        s = {
            "id": self.store.next_id(), "name": name.strip(),
            "roll_number": roll_number.strip(), "subjects": {},
            "total_marks": 0, "percentage": 0.0,
            "grade": "N/A", "status": "pending",
        }
        self.bus.publish("StudentCreated", {"student": s})
        return self.store.get(s["id"])

    def add_marks(self, sid: int, subject: str, marks: float) -> dict:
        s = self.store.get(sid)
        if s is None:
            raise ValueError(f"Student {sid} not found")
        if marks < 0 or marks > MAX_MARKS_PER_SUBJECT:
            raise ValueError(f"Marks must be between 0 and {MAX_MARKS_PER_SUBJECT}")
        if not subject or not subject.strip():
            raise ValueError("Subject name cannot be empty")
        new_subjects = dict(s["subjects"])
        new_subjects[subject.strip()] = marks
        self.bus.publish("MarksAdded", {"sid": sid, "subjects": new_subjects})
        return self.store.get(sid)

    def calculate_total_marks(self, sid: int) -> float:
        s = self.store.get(sid)
        if s is None: raise ValueError(f"Student {sid} not found")
        return s["total_marks"]

    def calculate_percentage(self, sid: int) -> float:
        s = self.store.get(sid)
        if s is None: raise ValueError(f"Student {sid} not found")
        return s["percentage"]

    def get_grade(self, sid: int) -> str:
        s = self.store.get(sid)
        if s is None: raise ValueError(f"Student {sid} not found")
        return s["grade"]

    def generate_result(self, sid: int) -> dict:
        s = self.store.get(sid)
        if s is None: raise ValueError(f"Student {sid} not found")
        return {
            "id": s["id"], "name": s["name"], "roll_number": s["roll_number"],
            "subjects": s["subjects"], "total_marks": s["total_marks"],
            "percentage": s["percentage"], "grade": s["grade"], "status": s["status"],
        }

    def get_student(self, sid: int) -> dict:
        s = self.store.get(sid)
        if s is None: raise ValueError(f"Student {sid} not found")
        return s

    def get_all_students(self) -> list[dict]:
        return self.store.get_all()
