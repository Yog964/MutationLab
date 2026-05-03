# Calculator — Microservices Architecture (Services + Gateway)

class ArithmeticService:
    def add(self, a, b):      return a + b
    def subtract(self, a, b): return a - b
    def multiply(self, a, b): return a * b
    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    def power(self, base, exp): return base ** exp
    def modulo(self, a, b):
        if b == 0:
            raise ValueError("Cannot modulo by zero")
        return a % b


class AdvancedService:
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

    def max_of_three(self, a, b, c):
        if a >= b and a >= c:
            return a
        if b >= a and b >= c:
            return b
        return c


class GradingService:
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


class CalculatorGateway:
    def __init__(self):
        self.arithmetic = ArithmeticService()
        self.advanced = AdvancedService()
        self.grading = GradingService()
        self.history = []

    def _log(self, op, result):
        self.history.append({"op": op, "result": result})


class CalculatorController:
    def __init__(self):
        self.gw = CalculatorGateway()

    def add(self, a, b):
        r = self.gw.arithmetic.add(a, b)
        self.gw._log("add", r)
        return r

    def subtract(self, a, b):   return self.gw.arithmetic.subtract(a, b)
    def multiply(self, a, b):   return self.gw.arithmetic.multiply(a, b)
    def divide(self, a, b):     return self.gw.arithmetic.divide(a, b)
    def power(self, base, exp): return self.gw.arithmetic.power(base, exp)
    def modulo(self, a, b):     return self.gw.arithmetic.modulo(a, b)
    def factorial(self, n):     return self.gw.advanced.factorial(n)
    def is_even(self, n):       return self.gw.advanced.is_even(n)
    def celsius_to_fahrenheit(self, c): return self.gw.advanced.celsius_to_fahrenheit(c)
    def grade(self, score):     return self.gw.grading.grade(score)
    def max_of_three(self, a, b, c): return self.gw.advanced.max_of_three(a, b, c)
    def get_history(self):      return self.gw.history
