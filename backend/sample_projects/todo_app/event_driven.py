# Todo — Event-Driven Architecture
class EventBus:
    def __init__(self): self._h = {}; self.log = []
    def on(self, e, fn): self._h.setdefault(e, []).append(fn)
    def emit(self, e, d): self.log.append({"event": e}); [fn(d) for fn in self._h.get(e, [])]

class TaskStore:
    def __init__(self, bus):
        self.bus = bus; self.tasks = {}; self._nid = 1
    def add(self, title, priority):
        if priority < 1 or priority > 5: raise ValueError("Priority must be 1-5")
        tid = self._nid; self._nid += 1
        self.tasks[tid] = {"id": tid, "title": title, "priority": priority, "done": False}
        self.bus.emit("task_added", {"id": tid}); return tid
    def get(self, tid):
        t = self.tasks.get(tid)
        if not t: raise ValueError("Task not found")
        return t
    def remove(self, tid):
        self.get(tid); del self.tasks[tid]; self.bus.emit("task_deleted", {"id": tid}); return True

class TodoController:
    def __init__(self):
        self.bus = EventBus(); self.store = TaskStore(self.bus)
    def add_task(self, title, p): return self.store.add(title, p)
    def complete_task(self, tid):
        t = self.store.get(tid); t["done"] = True
        self.bus.emit("task_completed", {"id": tid}); return True
    def delete_task(self, tid): return self.store.remove(tid)
    def get_task(self, tid): return dict(self.store.get(tid))
    def count_pending(self): return sum(1 for t in self.store.tasks.values() if not t["done"])
    def count_completed(self): return sum(1 for t in self.store.tasks.values() if t["done"])
    def get_high_priority(self): return [t for t in self.store.tasks.values() if t["priority"] >= 4]
    def is_all_done(self):
        tasks = list(self.store.tasks.values())
        if not tasks: return True
        return all(t["done"] for t in tasks)
    def completion_rate(self):
        tasks = list(self.store.tasks.values())
        if not tasks: return 0.0
        done = sum(1 for t in tasks if t["done"])
        return done / len(tasks) * 100
