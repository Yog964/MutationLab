# Tests for Calculator — all architectures use same interface
import os, importlib, pytest

arch = os.environ.get('TEST_ARCH', 'layered')
mod = importlib.import_module(arch)
Controller = mod.CalculatorController


class TestCalculator:
    def setup_method(self):
        self.c = Controller()

    def test_add_positive(self):        assert self.c.add(2, 3) == 5
    def test_add_negative(self):        assert self.c.add(-1, -1) == -2
    def test_add_zero(self):            assert self.c.add(0, 0) == 0
    def test_subtract(self):            assert self.c.subtract(10, 4) == 6
    def test_subtract_negative(self):   assert self.c.subtract(3, 7) == -4
    def test_multiply(self):            assert self.c.multiply(3, 4) == 12
    def test_multiply_zero(self):       assert self.c.multiply(5, 0) == 0
    def test_divide(self):              assert self.c.divide(10, 2) == 5.0
    def test_divide_fraction(self):     assert self.c.divide(7, 2) == 3.5

    def test_divide_by_zero(self):
        with pytest.raises(ValueError):
            self.c.divide(1, 0)

    def test_power(self):               assert self.c.power(2, 3) == 8
    def test_power_zero(self):          assert self.c.power(5, 0) == 1

    def test_modulo(self):              assert self.c.modulo(10, 3) == 1
    def test_modulo_by_zero(self):
        with pytest.raises(ValueError):
            self.c.modulo(5, 0)

    def test_factorial_zero(self):      assert self.c.factorial(0) == 1
    def test_factorial_five(self):      assert self.c.factorial(5) == 120
    def test_factorial_negative(self):
        with pytest.raises(ValueError):
            self.c.factorial(-1)

    def test_is_even_true(self):        assert self.c.is_even(4) is True
    def test_is_even_false(self):       assert self.c.is_even(7) is False

    def test_celsius_boiling(self):     assert self.c.celsius_to_fahrenheit(100) == 212
    def test_celsius_freezing(self):    assert self.c.celsius_to_fahrenheit(0) == 32

    def test_grade_a(self):             assert self.c.grade(95) == "A"
    def test_grade_b(self):             assert self.c.grade(85) == "B"
    def test_grade_c(self):             assert self.c.grade(75) == "C"
    def test_grade_d(self):             assert self.c.grade(65) == "D"
    def test_grade_f(self):             assert self.c.grade(45) == "F"
    def test_grade_invalid(self):
        with pytest.raises(ValueError):
            self.c.grade(110)

    def test_max_first(self):           assert self.c.max_of_three(9, 5, 3) == 9
    def test_max_second(self):          assert self.c.max_of_three(1, 8, 3) == 8
    def test_max_third(self):           assert self.c.max_of_three(1, 2, 7) == 7
