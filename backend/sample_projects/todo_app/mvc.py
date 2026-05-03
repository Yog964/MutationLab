# Todo — MVC Architecture
class TaskModel:
    def __init__(self): self.tasks = {}; self._nid = 1
    def create(self, title, priority):
        if priority < 1 or priority > 5: raise ValueError("Priority must be 1-5")
        tid = self._nid; self._nid += 1
        self.tasks[tid] = {"id": tid, "title": title, "priority": priority, "done": False}; return tid
    def find(self, tid):
        t = self.tasks.get(tid)
        if not t: raise ValueError("Task not found")
        return t
    def remove(self, tid): self.find(tid); del self.tasks[tid]; return True
    def all(self): return list(self.tasks.values())

class TaskView:
    def format(self, task): return dict(task)

class TodoController:
    def __init__(self): self.model = TaskModel(); self.view = TaskView()
    def add_task(self, title, priority): return self.model.create(title, priority)
    def complete_task(self, tid): t = self.model.find(tid); t["done"] = True; return True
    def delete_task(self, tid): return self.model.remove(tid)
    def get_task(self, tid): return dict(self.model.find(tid))
    def count_pending(self): return sum(1 for t in self.model.all() if not t["done"])
    def count_completed(self): return sum(1 for t in self.model.all() if t["done"])
    def get_high_priority(self): return [t for t in self.model.all() if t["priority"] >= 4]
    def is_all_done(self):
        tasks = self.model.all()
        if not tasks: return True
        return all(t["done"] for t in tasks)
    def completion_rate(self):
        tasks = self.model.all()
        if not tasks: return 0.0
        done = sum(1 for t in tasks if t["done"])
        return done / len(tasks) * 100
