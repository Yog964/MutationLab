# Calculator — MVC Architecture (Model / View / Controller)

class CalculatorModel:
    def __init__(self):
        self.history = []
        self.last_result = None

    def compute_add(self, a, b):
        self.last_result = a + b
        self.history.append({"op": "add", "result": self.last_result})
        return self.last_result

    def compute_subtract(self, a, b):
        self.last_result = a - b
        self.history.append({"op": "sub", "result": self.last_result})
        return self.last_result

    def compute_multiply(self, a, b):
        self.last_result = a * b
        return self.last_result

    def compute_divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        self.last_result = a / b
        return self.last_result

    def compute_power(self, base, exp):
        self.last_result = base ** exp
        return self.last_result

    def compute_modulo(self, a, b):
        if b == 0:
            raise ValueError("Cannot modulo by zero")
        self.last_result = a % b
        return self.last_result

    def compute_factorial(self, n):
        if n < 0:
            raise ValueError("Negative factorial")
        result = 1
        for i in range(1, n + 1):
            result = result * i
        self.last_result = result
        return result

    def check_even(self, n):
        return n % 2 == 0

    def convert_celsius(self, c):
        return c * 9 / 5 + 32

    def compute_grade(self, score):
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

    def find_max(self, a, b, c):
        if a >= b and a >= c:
            return a
        if b >= a and b >= c:
            return b
        return c


class CalculatorView:
    def format_result(self, op, result):
        return {"operation": op, "result": result}


class CalculatorController:
    def __init__(self):
        self.model = CalculatorModel()
        self.view = CalculatorView()

    def add(self, a, b):
        return self.model.compute_add(a, b)

    def subtract(self, a, b):
        return self.model.compute_subtract(a, b)

    def multiply(self, a, b):
        return self.model.compute_multiply(a, b)

    def divide(self, a, b):
        return self.model.compute_divide(a, b)

    def power(self, base, exp):
        return self.model.compute_power(base, exp)

    def modulo(self, a, b):
        return self.model.compute_modulo(a, b)

    def factorial(self, n):
        return self.model.compute_factorial(n)

    def is_even(self, n):
        return self.model.check_even(n)

    def celsius_to_fahrenheit(self, c):
        return self.model.convert_celsius(c)

    def grade(self, score):
        return self.model.compute_grade(score)

    def max_of_three(self, a, b, c):
        return self.model.find_max(a, b, c)

    def get_history(self):
        return self.model.history
