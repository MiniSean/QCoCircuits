import unittest
from qce_circuit.structure.intrf_circuit_operation_composite import (
    CircuitCompositeOperation,
)


class CompositeOperationTestCase(unittest.TestCase):

    # region Setup
    @classmethod
    def setUpClass(cls) -> None:
        """Set up for all test cases"""
        pass

    def setUp(self) -> None:
        """Set up for every test case"""
        pass
    # endregion

    # region Test Cases
    def test_empty_operation_duration_error(self):
        """Tests error when attempting to get operation duration of an empty composite operation."""
        operation = CircuitCompositeOperation()
        duration: float = operation.duration
        self.assertEqual(duration, 0.0)
    # endregion

    # region Teardown
    @classmethod
    def tearDownClass(cls) -> None:
        """Closes any left over processes after testing"""
        pass
    # endregion
