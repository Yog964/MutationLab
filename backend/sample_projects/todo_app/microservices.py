# Todo — Microservices Architecture
class TaskCatalogService:
    def __init__(self): self.tasks = {}; self._nid = 1
    def create(self, title, priority):
        if priority < 1 or priority > 5: raise ValueError("Priority must be 1-5")
        tid = self._nid; self._nid += 1
        self.tasks[tid] = {"id": tid, "title": title, "priority": priority, "done": False}; return tid
    def get(self, tid):
        t = self.tasks.get(tid)
        if not t: raise ValueError("Task not found")
        return t
    def remove(self, tid): self.get(tid); del self.tasks[tid]; return True
    def all(self): return list(self.tasks.values())

class TaskStatusService:
    def __init__(self, catalog): self.catalog = catalog
    def complete(self, tid): t = self.catalog.get(tid); t["done"] = True; return True
    def pending_count(self): return sum(1 for t in self.catalog.all() if not t["done"])
    def completed_count(self): return sum(1 for t in self.catalog.all() if t["done"])
    def all_done(self):
        tasks = self.catalog.all()
        if not tasks: return True
        return all(t["done"] for t in tasks)
    def rate(self):
        tasks = self.catalog.all()
        if not tasks: return 0.0
        done = sum(1 for t in tasks if t["done"])
        return done / len(tasks) * 100

class PriorityService:
    def __init__(self, catalog): self.catalog = catalog
    def high(self): return [t for t in self.catalog.all() if t["priority"] >= 4]

class TodoController:
    def __init__(self):
        self.catalog = TaskCatalogService()
        self.status = TaskStatusService(self.catalog)
        self.priority = PriorityService(self.catalog)
    def add_task(self, title, p): return self.catalog.create(title, p)
    def complete_task(self, tid): return self.status.complete(tid)
    def delete_task(self, tid): return self.catalog.remove(tid)
    def get_task(self, tid): return dict(self.catalog.get(tid))
    def count_pending(self): return self.status.pending_count()
    def count_completed(self): return self.status.completed_count()
    def get_high_priority(self): return self.priority.high()
    def is_all_done(self): return self.status.all_done()
    def completion_rate(self): return self.status.rate()
