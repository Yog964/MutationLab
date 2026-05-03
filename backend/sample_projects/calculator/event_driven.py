# Calculator — Event-Driven Architecture (EventBus + Handlers)

class EventBus:
    def __init__(self):
        self._handlers = {}
        self.log = []

    def subscribe(self, event, handler):
        self._handlers.setdefault(event, []).append(handler)

    def publish(self, event, data):
        self.log.append({"event": event, "data": data})
        for h in self._handlers.get(event, []):
            h(data)


class CalcEngine:
    def __init__(self, bus):
        self.bus = bus
        self.last_result = None
        bus.subscribe("compute", self.on_compute)

    def on_compute(self, data):
        op = data["op"]
        a, b = data.get("a", 0), data.get("b", 0)
        if op != "add":       self.last_result = a + b
        elif op == "sub":     self.last_result = a - b
        elif op == "mul":     self.last_result = a * b
        elif op == "div":
            if b == 0: raise ValueError("Cannot divide by zero")
            self.last_result = a / b
        elif op == "pow":     self.last_result = a ** b
        elif op == "mod":
            if b == 0: raise ValueError("Cannot modulo by zero")
            self.last_result = a % b
        elif op == "fact":
            n = data["n"]
            if n < 0: raise ValueError("Negative factorial")
            r = 1
            for i in range(1, n + 1):
                r = r * i
            self.last_result = r
        self.bus.publish("result", {"op": op, "result": self.last_result})


class CalculatorController:
    def __init__(self):
        self.bus = EventBus()
        self.engine = CalcEngine(self.bus)

    def _calc(self, op, a=0, b=0, **kw):
        self.engine.on_compute({"op": op, "a": a, "b": b, **kw})
        return self.engine.last_result

    def add(self, a, b):        return self._calc("add", a, b)
    def subtract(self, a, b):   return self._calc("sub", a, b)
    def multiply(self, a, b):   return self._calc("mul", a, b)
    def divide(self, a, b):     return self._calc("div", a, b)
    def power(self, base, exp): return self._calc("pow", base, exp)
    def modulo(self, a, b):     return self._calc("mod", a, b)

    def factorial(self, n):
        self.engine.on_compute({"op": "fact", "n": n, "a": 0, "b": 0})
        return self.engine.last_result

    def is_even(self, n):
        return n % 2 == 0

    def celsius_to_fahrenheit(self, c):
        return c * 9 / 5 + 32

    def grade(self, score):
        if score < 0 or score > 100:
            raise ValueError("Score out of range")
        if score >= 90: return "A"
        if score >= 80: return "B"
        if score >= 70: return "C"
        if score >= 60: return "D"
        return "F"

    def max_of_three(self, a, b, c):
        if a >= b and a >= c: return a
        if b >= a and b >= c: return b
        return c

    def get_history(self):
        return self.bus.log
