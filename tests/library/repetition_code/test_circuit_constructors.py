import unittest
from typing import List
from numpy.testing import assert_array_equal
from qce_circuit.connectivity.intrf_channel_identifier import IQubitID, QubitIDObj
from qce_circuit.visualization.visualize_circuit.display_circuit import plot_circuit
from qce_circuit.language import (
    InitialStateContainer,
    InitialStateEnum,
)
from qce_circuit.library.repetition_code.repetition_code_connectivity import Repetition9Code
from qce_circuit.library.repetition_code.circuit_components import RepetitionCodeDescription
from qce_circuit.library.repetition_code.circuit_constructors import (
    construct_repetition_code_circuit_simplified,
    construct_repetition_code_circuit,
)
import matplotlib.pyplot as plt


class RepetitionCodeCircuitConstructorsTestCase(unittest.TestCase):

    # region Setup
    @classmethod
    def setUpClass(cls) -> None:
        """Set up for all test cases"""
        # Note, initial state only describes data-qubit states at the moment
        cls.initial_state: InitialStateContainer = InitialStateContainer.from_ordered_list([
            InitialStateEnum.ZERO,
            InitialStateEnum.ZERO,
            InitialStateEnum.ZERO,
        ])
        cls.involved_qubit_ids: List[IQubitID] = [
            QubitIDObj('D7'),
            QubitIDObj('Z3'),
            QubitIDObj('D4'),
            QubitIDObj('Z1'),
            QubitIDObj('D5'),
        ]

    def setUp(self) -> None:
        """Set up for every test case"""
        pass
    # endregion

    # region Test Cases
    def test_construct_from_arbitrary_chain_length(self):
        """Tests construction from arbitrary chain length."""
        circuit_description: RepetitionCodeDescription = RepetitionCodeDescription.from_chain(
            length=5
        )
        assert_array_equal(
            circuit_description.qubit_indices,
            [0, 1, 2, 3, 4],
        )
        assert_array_equal(
            circuit_description.data_qubit_indices,
            [0, 2, 4],
        )
        assert_array_equal(
            circuit_description.ancilla_qubit_indices,
            [1, 3],
        )
        self.assertEqual(
            circuit_description.gate_sequence_count,
            2,
            msg="Expects a gate-sequence depth of 2 for arbitrary connectivity."
        )
        circuit = construct_repetition_code_circuit(
            description=circuit_description,
            qec_cycles=1,
        )
        self.assertIsNotNone(circuit)
        plot_circuit(circuit, channel_map=circuit_description.circuit_channel_map)
        self.assertTrue(True)

    def test_construct_from_arbitrary_initial_state(self):
        """Tests construction from arbitrary initial state (defining the chain length)."""
        circuit_description: RepetitionCodeDescription = RepetitionCodeDescription.from_initial_state(
            initial_state=self.initial_state,
        )
        assert_array_equal(
            circuit_description.qubit_indices,
            [0, 1, 2, 3, 4],
        )
        assert_array_equal(
            circuit_description.data_qubit_indices,
            [0, 2, 4],
        )
        assert_array_equal(
            circuit_description.ancilla_qubit_indices,
            [1, 3],
        )
        self.assertEqual(
            circuit_description.gate_sequence_count,
            2,
            msg="Expects a gate-sequence depth of 2 for arbitrary connectivity."
        )
        circuit = construct_repetition_code_circuit(
            description=circuit_description,
            qec_cycles=3,
            initial_state=self.initial_state,
        )
        self.assertIsNotNone(circuit)
        plot_circuit(circuit, channel_map=circuit_description.circuit_channel_map)
        self.assertTrue(True)

    def test_construct_from_connectivity(self):
        """Tests circuit construction from Surface-17 connectivity constraints."""
        circuit_description: RepetitionCodeDescription = RepetitionCodeDescription.from_connectivity(
            involved_qubit_ids=self.involved_qubit_ids,
            connectivity=Repetition9Code(),
        )
        assert_array_equal(
            circuit_description.qubit_indices,
            [0, 1, 2, 3, 4],
        )
        assert_array_equal(
            circuit_description.data_qubit_indices,
            [0, 2, 4],
        )
        assert_array_equal(
            circuit_description.ancilla_qubit_indices,
            [1, 3],
        )
        self.assertEqual(
            circuit_description.gate_sequence_count,
            4,
            msg="Expects a gate-sequence depth of 4 for Surface-17 connectivity."
        )
        circuit = construct_repetition_code_circuit(
            description=circuit_description,
            qec_cycles=6,
            initial_state=self.initial_state,
        )
        self.assertIsNotNone(circuit)
        plot_circuit(circuit, channel_map=circuit_description.circuit_channel_map)
        self.assertTrue(True)

    def test_construct_simplified(self):
        """Tests simplified circuit construction."""
        circuit_description: RepetitionCodeDescription = RepetitionCodeDescription.from_connectivity(
            involved_qubit_ids=self.involved_qubit_ids,
            connectivity=Repetition9Code(),
        )
        circuit = construct_repetition_code_circuit_simplified(
            description=circuit_description,
            qec_cycles=9,
            initial_state=self.initial_state,
        )
        self.assertIsNotNone(circuit)
        plot_circuit(circuit, channel_map=circuit_description.circuit_channel_map)
        self.assertTrue(True)
    # endregion

    # region Teardown
    @classmethod
    def tearDownClass(cls) -> None:
        """Closes any left over processes after testing"""
        plt.close('all')
    # endregion
