from typing import Generic, TypeVar
import pytest
from app.infrastructure.typechecked import typechecked

T1 = TypeVar("T1")
T2 = TypeVar("T2")

class TestTypechecked:
    class class_1():
        @typechecked
        def __init__(self, a: str) -> None:
            self.a = a

    class class_2():
        @typechecked
        def __init__(self, a: str) -> None:
            self.a = a

    class class_3(Generic[T1]):
        def __init__(self, a: T1) -> None:
            self.a = a
            super().__init__()

    class class_4(Generic[T1, T2]):
        def __init__(self, a: T1, b: T2) -> None:
            self.a = a
            self.b = b
            super().__init__()

    class class_5(class_1, class_2):
        def __init__(self, a: str) -> None:
            super().__init__(a)

    @typechecked
    def function_1(self):
        pass

    @typechecked
    def function_2(self, a: int):
        pass

    @typechecked
    def function_3(self, a: int | str):
        pass

    @typechecked
    def function_4(self) -> int:
        pass

    @typechecked
    def function_5(self) -> int:
        return "a"

    @typechecked
    def function_6(self, a: class_1):
        pass

    @typechecked
    def function_7(self, a: class_3[str]) -> str:
        return a.a

    @typechecked
    def function_8(self, a: class_4[str, int]) -> int:
        return a.b

    @typechecked
    def function_9(self, a: class_4[class_4[int, str], int]) -> int:
        return a.b

    @typechecked
    def function_10(self, a: class_1) -> str:
        return a.a

    @typechecked
    def function_11(self, a: class_2) -> str:
        return a.a

    def test_1_typechecked_no_parameters(self):
        # Act / Assert
        self.function_1()

    def test_1_typechecked_too_many_parameters(self):
        # Arrange
        param_1 = 1
        # Act / Assert
        with pytest.raises(Exception):
            self.function_1(param_1)

    def test_2_typechecked_missing_parameter(self):
        # Act / Assert
        with pytest.raises(Exception):
            self.function_2()

    def test_2_typechecked_correct_parameter(self):
        # Arrange
        a: int = 1
        # Act / Assert
        self.function_2(a)

    def test_2_typechecked_incorrect_parameter_type(self):
        # Arrange
        a: str = "a"
        # Act / Assert
        with pytest.raises(TypeError):
            self.function_2(a)

    def test_2_typechecked_missing_parameter(self):
        # Act / Assert
        with pytest.raises(ValueError):
            self.function_2()

    def test_3_typechecked_correct_parameter_int(self):
        # Arrange
        a: int = 1
        # Act / Assert
        self.function_3(a)

    def test_3_typechecked_correct_parameter_str(self):
        # Arrange
        a: str = "1"
        # Act / Assert
        self.function_3(a)

    def test_3_typechecked_incorrect_parameter_type(self):
        # Arrange
        a: float = 1.2
        # Act / Assert
        with pytest.raises(TypeError):
            self.function_3(a)

    def test_4_typechecked_missing_return_value(self):
        # Act / Assert
        with pytest.raises(TypeError):
            self.function_4()

    def test_5_typechecked_incorrect_return_value_type(self):
        # Act / Assert
        with pytest.raises(TypeError):
            self.function_5()

    def test_function_6_typechecked_correct_class_instance(self):
        # Arrange
        a = self.class_1("a")
        # Act / Assert
        self.function_6(a)

    def test_function_6_typechecked_incorrect_class_instance_type(self):
        # Arrange
        a = self.class_2("a")
        # Act / Assert
        with pytest.raises(TypeError):
            self.function_6(a)

    def test_function_7_typechecked_correct_class_generic_argument(self):
        # Arrange
        a = self.class_3[str]("a")
        # Act / Assert
        self.function_7(a)

    def test_function_7_typechecked_incorrect_class_generic_argument(self):
        # Arrange
        a = self.class_3[int](1)
        # Act / Assert
        with pytest.raises(TypeError):
            self.function_7(a)

    def test_function_8_typechecked_correct_class_generic_argument(self):
        # Arrange
        a = self.class_4[str, int]("a", 2)
        # Act / Assert
        self.function_8(a)

    def test_function_8_typechecked_incorrect_class_generic_argument(self):
        # Arrange
        a = self.class_4[str, str]("a", "b")
        # Act / Assert
        with pytest.raises(TypeError):
            self.function_8(a)

    def test_function_9_typechecked_correct_class_generic_argument(self):
        # Arrange
        a = self.class_4[self.class_4[int, str], int](self.class_4[int, str](1, "a"), 1)
        # Act / Assert
        self.function_9(a)

    def test_function_9_typechecked_incorrect_class_generic_argument(self):
        # Arrange
        a = self.class_4[self.class_4[int, str], str](self.class_4[str, str]("a", "b"), "2")
        # Act / Assert
        with pytest.raises(TypeError):
            self.function_9(a)

    def test_function_10_typechecked_inheritanceclass_5_to_class_1(self):
        # Arrange
        a = self.class_5("a")
        # Act / Assert
        self.function_10(a)

    def test_function_10_typechecked_inheritanceclass_5_to_class_2(self):
        # Arrange
        a = self.class_5("a")
        # Act / Assert
        self.function_11(a)