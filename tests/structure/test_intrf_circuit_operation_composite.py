import unittest
from qce_circuit.language.declarative_circuit import DeclarativeCircuit
from qce_circuit.structure.circuit_operations import (
    Reset,
    Rx180,
)
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


class DecompositionBugTestCase(unittest.TestCase):
    """
    Test case module specifically made to monitor a known bug.
    It is best described when constructing a circuit from multiple sub-circuits.
    When executing the decomposition of one of the sub-circuits before finishing construction of the main circuit,
    then the main circuit drops all subsequent operations after last (directly added) operation from main circuit.

    Further investigation shows that this likely comes from the following situation.

    # --- Circuit after normal composition ---
    Operation("A") - None [Ref]
    CompOperation("B") - "A" [Head]
     - Operation("C") - None [Ref]
    # ----------------------------------------

    When running decomposition on 'CompOperation' (B), the child nodes with no link (C) are forced to carry [Head] relation.
    This is intended because if the 'CompOperation' is nested, it should correctly pass its relation to the first child nodes (connected to the graph root).

    # --- Circuit after decomposition --------
    Operation("A") - None [Ref]
    CompOperation("B") - "A" [Head]
     - Operation("C") - "A" [Ref]
    # ----------------------------------------
    """

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
    def test_intended_behaviour(self):
        """Tests intended behaviour case 1."""
        main_circuit = DeclarativeCircuit()
        sub_circuit = DeclarativeCircuit()
        operation_a = Reset(0)
        operation_b = Rx180(0)

        sub_circuit.add(operation_a)

        sub_sub_circuit = DeclarativeCircuit()
        sub_sub_circuit.add(operation_b)
        sub_circuit.add(sub_sub_circuit)

        # It matters if decomposition is done before applying circuit to main circuit
        sub_circuit.circuit_structure.decomposed_operations()

        main_circuit.add(sub_circuit)

        self.assertListEqual(
            [operation.__class__ for operation in main_circuit.operations],
            [Reset, Rx180]
        )
    # endregion

    # region Teardown
    @classmethod
    def tearDownClass(cls) -> None:
        """Closes any left over processes after testing"""
        pass
    # endregion