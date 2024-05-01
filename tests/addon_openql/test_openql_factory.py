import unittest
from qce_circuit.language.declarative_circuit import DeclarativeCircuit
from qce_circuit.structure.circuit_operations import (
    Rx180,
    Barrier,
    DispersiveMeasure,
)
from qce_circuit.addon_openql.factory_manager import to_openql
from qce_circuit.addon_stim.factory_manager import to_stim


class OpenQLFactoryTestCase(unittest.TestCase):

    # region Setup
    @classmethod
    def setUpClass(cls) -> None:
        """Set up for all test cases"""
        circuit = DeclarativeCircuit()
        circuit.add(Rx180(0))
        # circuit.add(Barrier([0]))
        circuit.add(DispersiveMeasure(0, acquisition_strategy=circuit.get_acquisition_strategy()))
        cls.circuit = circuit

    def setUp(self) -> None:
        """Set up for every test case"""
        pass
    # endregion

    # region Test Cases
    def test_default(self):
        """Tests default True."""
        print(to_stim(self.circuit).__repr__())
        response = to_openql(self.circuit)
        print(response)
        self.assertTrue(True)
    # endregion

    # region Teardown
    @classmethod
    def tearDownClass(cls) -> None:
        """Closes any left over processes after testing"""
        pass
    # endregion
