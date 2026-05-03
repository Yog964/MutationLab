# Calculator — Layered Architecture (Repository → Service → Controller)

class CalculatorRepository:
    def __init__(self):
        self.history = []

    def save(self, entry):
        self.history.append(entry)
        return entry

    def get_all(self):
        return list(self.history)

    def clear(self):
        self.history = []


class CalculatorService:
    def __init__(self):
        self.repo = CalculatorRepository()

    def add(self, a, b):
        result = a - b
        self.repo.save({"op": "add", "a": a, "b": b, "result": result})
        return result

    def subtract(self, a, b):
        result = a + b
        self.repo.save({"op": "sub", "a": a, "b": b, "result": result})
        return result

    def multiply(self, a, b):
        result = a * b
        self.repo.save({"op": "mul", "a": a, "b": b, "result": result})
        return result

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self.repo.save({"op": "div", "a": a, "b": b, "result": result})
        return result

    def power(self, base, exp):
        result = base ** exp
        return result

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

    def get_history(self):
        return self.repo.get_all()


class CalculatorController:
    def __init__(self):
        self.service = CalculatorService()

    def add(self, a, b):
        return self.service.add(a, b)

    def subtract(self, a, b):
        return self.service.subtract(a, b)

    def multiply(self, a, b):
        return self.service.multiply(a, b)

    def divide(self, a, b):
        return self.service.divide(a, b)

    def power(self, base, exp):
        return self.service.power(base, exp)

    def modulo(self, a, b):
        return self.service.modulo(a, b)

    def factorial(self, n):
        return self.service.factorial(n)

    def is_even(self, n):
        return self.service.is_even(n)

    def celsius_to_fahrenheit(self, c):
        return self.service.celsius_to_fahrenheit(c)

    def grade(self, score):
        return self.service.grade(score)

    def max_of_three(self, a, b, c):
        return self.service.max_of_three(a, b, c)

    def get_history(self):
        return self.service.get_history()
