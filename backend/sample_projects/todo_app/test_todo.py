import os, importlib, pytest
arch = os.environ.get('TEST_ARCH', 'layered')
mod = importlib.import_module(arch)
Controller = mod.TodoController

class TestTodo:
    def setup_method(self): self.todo = Controller()

    def test_add_task(self):
        tid = self.todo.add_task("Buy groceries", 3)
        assert tid >= 1
    def test_add_invalid_priority(self):
        with pytest.raises(ValueError): self.todo.add_task("X", 0)
    def test_add_high_priority(self):
        with pytest.raises(ValueError): self.todo.add_task("X", 6)
    def test_get_task(self):
        tid = self.todo.add_task("Read", 2)
        t = self.todo.get_task(tid)
        assert t["title"] == "Read" and t["done"] is False
    def test_complete_task(self):
        tid = self.todo.add_task("Run", 4)
        assert self.todo.complete_task(tid) is True
        assert self.todo.get_task(tid)["done"] is True
    def test_complete_invalid(self):
        with pytest.raises(ValueError): self.todo.complete_task(9999)
    def test_delete_task(self):
        tid = self.todo.add_task("Sleep", 1)
        assert self.todo.delete_task(tid) is True
    def test_delete_invalid(self):
        with pytest.raises(ValueError): self.todo.delete_task(9999)
    def test_count_pending(self):
        self.todo.add_task("A", 1); self.todo.add_task("B", 2)
        tid = self.todo.add_task("C", 3); self.todo.complete_task(tid)
        assert self.todo.count_pending() == 2
    def test_count_completed(self):
        t1 = self.todo.add_task("A", 1); self.todo.complete_task(t1)
        self.todo.add_task("B", 2)
        assert self.todo.count_completed() == 1
    def test_high_priority(self):
        self.todo.add_task("Low", 1); self.todo.add_task("High", 5)
        hp = self.todo.get_high_priority()
        assert len(hp) == 1 and hp[0]["priority"] == 5
    def test_is_all_done_empty(self):
        assert self.todo.is_all_done() is True
    def test_is_all_done_false(self):
        self.todo.add_task("X", 1)
        assert self.todo.is_all_done() is False
    def test_is_all_done_true(self):
        tid = self.todo.add_task("X", 1); self.todo.complete_task(tid)
        assert self.todo.is_all_done() is True
    def test_completion_rate_empty(self):
        assert self.todo.completion_rate() == 0.0
    def test_completion_rate_half(self):
        t1 = self.todo.add_task("A", 1); self.todo.add_task("B", 2)
        self.todo.complete_task(t1)
        assert self.todo.completion_rate() == 50.0
