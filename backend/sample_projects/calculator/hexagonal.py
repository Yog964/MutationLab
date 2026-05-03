# Calculator — Hexagonal Architecture (Domain → Port → Adapter)
from abc import ABC, abstractmethod


class CalcEntity:
    def __init__(self, a=0, b=0):
        self.a = a
        self.b = b
        self.result = None


class CalcPort(ABC):
    @abstractmethod
    def save_result(self, entry): ...
    @abstractmethod
    def get_results(self): ...


class InMemoryAdapter(CalcPort):
    def __init__(self):
        self.store = []

    def save_result(self, entry):
        self.store.append(entry)
        return entry

    def get_results(self):
        return list(self.store)


class CalcUseCase:
    def __init__(self, adapter: CalcPort):
        self.adapter = adapter

    def add(self, a, b):
        result = a + b
        self.adapter.save_result({"op": "add", "result": result})
        return result

    def subtract(self, a, b):
        result = a - b
        return result

    def multiply(self, a, b):
        result = a * b
        return result

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

    def power(self, base, exp):
        return base ** exp

    def modulo(self, a, b):
        if b == 0:
            raise ValueError("Cannot modulo by zero")
        return a % b

    def factorial(self, n):
        if n < 0:
            raise ValueError("Negative factorial")
        result = 1
        for i in range(1, n + 1):
            result = result * i
        return result

    def is_even(self, n):
        return n % 2 == 0

    def celsius_to_fahrenheit(self, c):
        return c * 9 / 5 + 32

    def grade(self, score):
        if score < 0 or score > 100:
            raise ValueError("Score out of range")
        if score >= 90:
            return "A"
        if score >= 80:
            return "B"
        if score >= 70:
            return "C"
        if score >= 60:
            return "D"
        return "F"

    def max_of_three(self, a, b, c):
        if a >= b and a >= c:
            return a
        if b >= a and b >= c:
            return b
        return c


class CalculatorController:
    def __init__(self):
        self.use_case = CalcUseCase(InMemoryAdapter())

    def add(self, a, b):        return self.use_case.add(a, b)
    def subtract(self, a, b):   return self.use_case.subtract(a, b)
    def multiply(self, a, b):   return self.use_case.multiply(a, b)
    def divide(self, a, b):     return self.use_case.divide(a, b)
    def power(self, base, exp): return self.use_case.power(base, exp)
    def modulo(self, a, b):     return self.use_case.modulo(a, b)
    def factorial(self, n):     return self.use_case.factorial(n)
    def is_even(self, n):       return self.use_case.is_even(n)
    def celsius_to_fahrenheit(self, c): return self.use_case.celsius_to_fahrenheit(c)
    def grade(self, score):     return self.use_case.grade(score)
    def max_of_three(self, a, b, c): return self.use_case.max_of_three(a, b, c)
    def get_history(self):      return self.use_case.adapter.get_results()
