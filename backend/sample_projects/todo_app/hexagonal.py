# Todo — Hexagonal Architecture
from abc import ABC, abstractmethod

class TaskPort(ABC):
    @abstractmethod
    def save(self, task): ...
    @abstractmethod
    def find(self, tid): ...
    @abstractmethod
    def remove(self, tid): ...
    @abstractmethod
    def all(self): ...

class InMemoryAdapter(TaskPort):
    def __init__(self): self.store = {}; self._nid = 1
    def save(self, task):
        tid = self._nid; self._nid += 1
        task["id"] = tid; task["done"] = False; self.store[tid] = task; return tid
    def find(self, tid): return self.store.get(tid)
    def remove(self, tid):
        if tid in self.store: del self.store[tid]; return True
        return False
    def all(self): return list(self.store.values())

class TaskUseCase:
    def __init__(self, adapter): self.adapter = adapter
    def add_task(self, title, priority):
        if priority < 1 or priority > 5: raise ValueError("Priority must be 1-5")
        return self.adapter.save({"title": title, "priority": priority})
    def complete_task(self, tid):
        t = self.adapter.find(tid)
        if not t: raise ValueError("Task not found")
        t["done"] = True; return True
    def delete_task(self, tid):
        if not self.adapter.find(tid): raise ValueError("Task not found")
        return self.adapter.remove(tid)
    def get_task(self, tid):
        t = self.adapter.find(tid)
        if not t: raise ValueError("Task not found")
        return dict(t)
    def count_pending(self): return sum(1 for t in self.adapter.all() if not t["done"])
    def count_completed(self): return sum(1 for t in self.adapter.all() if t["done"])
    def get_high_priority(self): return [t for t in self.adapter.all() if t["priority"] >= 4]
    def is_all_done(self):
        tasks = self.adapter.all()
        if not tasks: return True
        return all(t["done"] for t in tasks)
    def completion_rate(self):
        tasks = self.adapter.all()
        if not tasks: return 0.0
        done = sum(1 for t in tasks if t["done"])
        return done / len(tasks) * 100

class TodoController:
    def __init__(self): self.uc = TaskUseCase(InMemoryAdapter())
    def add_task(self, title, p): return self.uc.add_task(title, p)
    def complete_task(self, tid): return self.uc.complete_task(tid)
    def delete_task(self, tid): return self.uc.delete_task(tid)
    def get_task(self, tid): return self.uc.get_task(tid)
    def count_pending(self): return self.uc.count_pending()
    def count_completed(self): return self.uc.count_completed()
    def get_high_priority(self): return self.uc.get_high_priority()
    def is_all_done(self): return self.uc.is_all_done()
    def completion_rate(self): return self.uc.completion_rate()
