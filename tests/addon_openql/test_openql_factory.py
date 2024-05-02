import unittest
from typing import List
from qce_circuit.language.declarative_circuit import DeclarativeCircuit
from qce_circuit.structure.circuit_operations import (
    DispersiveMeasure,
    Barrier,
    Wait,
    Reset,
    Rx180,
    Rx90,
    CPhase,
)
from qce_circuit.addon_openql.factory_manager import to_openql


class OpenQLFactoryTestCase(unittest.TestCase):

    # region Setup
    @classmethod
    def setUpClass(cls) -> None:
        """Set up for all test cases"""
        circuit = DeclarativeCircuit()
        circuit.add(Rx180(0))
        circuit.add(Barrier([0]))
        circuit.add(Wait(0))
        circuit.add(DispersiveMeasure(0, acquisition_strategy=circuit.get_acquisition_strategy()))
        cls.circuit = circuit
        cls.circuit_id: str = 'unit_test_circuit'

    def setUp(self) -> None:
        """Set up for every test case"""
        pass
    # endregion

    # region Test Cases
    def test_openql_program_construction(self):
        """Tests construction of example openql Program."""
        response = to_openql(self.circuit, circuit_id=self.circuit_id)
        # response.compile()
        self.assertTrue(True)

    def test_construct_conditional_oscillation(self):
        """Tests construction of example circuit."""
        all_qubit_idxs: List[int] = list(range(0, 17))
        target_idx: int = 8
        control_idx: int = 2
        spectator_idx: int = 0

        circuit = DeclarativeCircuit()
        circuit.add(Reset(target_idx))
        circuit.add(Reset(control_idx))
        circuit.add(Barrier(all_qubit_idxs))
        circuit.add(Rx90(target_idx))
        circuit.add(CPhase(control_idx, target_idx))
        circuit.add(Barrier(all_qubit_idxs))
        circuit.add(Rx90(target_idx))
        circuit.add(Barrier(all_qubit_idxs))
        circuit.add(DispersiveMeasure(target_idx, acquisition_strategy=circuit.get_acquisition_strategy()))
        circuit.add(DispersiveMeasure(control_idx, acquisition_strategy=circuit.get_acquisition_strategy()))

        response = to_openql(circuit, circuit_id='conditional_oscillation')
        # response.compile()
        self.assertTrue(True)
    # endregion

    # region Teardown
    @classmethod
    def tearDownClass(cls) -> None:
        """Closes any left over processes after testing"""
        pass
    # endregion
