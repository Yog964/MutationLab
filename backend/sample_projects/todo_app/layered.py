# Todo — Layered Architecture
class TaskRepository:
    def __init__(self): self.tasks = {}; self._nid = 1
    def save(self, task):
        tid = self._nid; self._nid += 1
        task["id"] = tid; task["done"] = False; self.tasks[tid] = task; return tid
    def get(self, tid): return self.tasks.get(tid)
    def delete(self, tid):
        if tid in self.tasks: del self.tasks[tid]; return True
        return False
    def all(self): return list(self.tasks.values())

class TaskService:
    def __init__(self): self.repo = TaskRepository()
    def add_task(self, title, priority):
        if priority < 1 or priority > 5: raise ValueError("Priority must be 1-5")
        return self.repo.save({"title": title, "priority": priority})
    def complete_task(self, tid):
        t = self.repo.get(tid)
        if not t: raise ValueError("Task not found")
        t["done"] = True; return True
    def delete_task(self, tid):
        if not self.repo.get(tid): raise ValueError("Task not found")
        return self.repo.delete(tid)
    def get_task(self, tid):
        t = self.repo.get(tid)
        if not t: raise ValueError("Task not found")
        return dict(t)
    def count_pending(self):
        return sum(1 for t in self.repo.all() if not t["done"])
    def count_completed(self):
        return sum(1 for t in self.repo.all() if t["done"])
    def get_high_priority(self):
        return [t for t in self.repo.all() if t["priority"] >= 4]
    def is_all_done(self):
        tasks = self.repo.all()
        if not tasks: return True
        return all(t["done"] for t in tasks)
    def completion_rate(self):
        tasks = self.repo.all()
        if not tasks: return 0.0
        done = sum(1 for t in tasks if t["done"])
        return done / len(tasks) * 100

class TodoController:
    def __init__(self): self.svc = TaskService()
    def add_task(self, title, priority): return self.svc.add_task(title, priority)
    def complete_task(self, tid): return self.svc.complete_task(tid)
    def delete_task(self, tid): return self.svc.delete_task(tid)
    def get_task(self, tid): return self.svc.get_task(tid)
    def count_pending(self): return self.svc.count_pending()
    def count_completed(self): return self.svc.count_completed()
    def get_high_priority(self): return self.svc.get_high_priority()
    def is_all_done(self): return self.svc.is_all_done()
    def completion_rate(self): return self.svc.completion_rate()
