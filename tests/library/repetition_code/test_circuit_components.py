import unittest
from collections import Counter
from typing import List
from qce_circuit.connectivity.intrf_channel_identifier import (
    IQubitID,
    QubitIDObj,
    IEdgeID,
    EdgeIDObj,
)
from qce_circuit.connectivity.generic_gate_sequence import (
    IGenericSurfaceCodeLayer,
    GenericSurfaceCode,
    GateSequenceLayer,
)
from qce_circuit.library.repetition_code.circuit_constructors import (
    IRepetitionCodeDescription,
    RepetitionCodeDescription,
)
from qce_circuit.library.repetition_code.repetition_code_connectivity import Repetition9Code


class CircuitDescriptionFromConnectivityTestCase(unittest.TestCase):

    # region Setup
    @classmethod
    def setUpClass(cls) -> None:
        """Set up for all test cases"""
        cls.layout = Repetition9Code()

    def setUp(self) -> None:
        """Set up for every test case"""
        pass
    # endregion

    # region Test Cases
    def test_example_repetition_code_z3z1(self):
        """Tests specific repetition-code (distance-3) Z3-Z1."""
        circuit_description = RepetitionCodeDescription.from_connectivity(
            involved_qubit_ids=[QubitIDObj('D7'), QubitIDObj('Z3'), QubitIDObj('D4'), QubitIDObj('Z1'), QubitIDObj('D5')],
            connectivity=self.layout,
        )
        sequence: IGenericSurfaceCodeLayer = circuit_description.to_sequence()

        # Sequence index 0
        park_identifiers: List[IQubitID] = [element.identifier for element in sequence.get_gate_sequence_at_index(0).park_operations]
        expected_identifiers: List[IQubitID] = [
            QubitIDObj('X3'),
            QubitIDObj('Z3'),
        ]
        self.assertEqual(
            Counter(park_identifiers), Counter(expected_identifiers),
            msg="Expects all identifiers to be present in park identifiers list.",
        )

        # Sequence index 1
        park_identifiers: List[IQubitID] = [element.identifier for element in sequence.get_gate_sequence_at_index(1).park_operations]
        expected_identifiers: List[IQubitID] = [
            QubitIDObj('X3'),
            QubitIDObj('Z4'),
            QubitIDObj('X2'),
        ]
        self.assertEqual(
            Counter(park_identifiers), Counter(expected_identifiers),
            msg="Expects all identifiers to be present in park identifiers list.",
        )

        # Sequence index 2
        park_identifiers: List[IQubitID] = [element.identifier for element in sequence.get_gate_sequence_at_index(2).park_operations]
        expected_identifiers: List[IQubitID] = [
        ]
        self.assertEqual(
            Counter(park_identifiers), Counter(expected_identifiers),
            msg="Expects all identifiers to be present in park identifiers list.",
        )

        # Sequence index 3
        park_identifiers: List[IQubitID] = [element.identifier for element in sequence.get_gate_sequence_at_index(3).park_operations]
        expected_identifiers: List[IQubitID] = [
            QubitIDObj('X3'),
            QubitIDObj('Z1'),
        ]
        self.assertEqual(
            Counter(park_identifiers), Counter(expected_identifiers),
            msg="Expects all identifiers to be present in park identifiers list.",
        )

    def test_example_repetition_code_z1z4(self):
        """Tests specific repetition-code (distance-3) Z1-Z4."""
        circuit_description = RepetitionCodeDescription.from_connectivity(
            involved_qubit_ids=[QubitIDObj('D4'), QubitIDObj('Z1'), QubitIDObj('D5'), QubitIDObj('Z4'), QubitIDObj('D6')],
            connectivity=self.layout,
        )
        sequence: IGenericSurfaceCodeLayer = circuit_description.to_sequence()

        # Sequence index 0
        park_identifiers: List[IQubitID] = [element.identifier for element in sequence.get_gate_sequence_at_index(0).park_operations]
        expected_identifiers: List[IQubitID] = [
            QubitIDObj('X3'),
            QubitIDObj('Z3'),
        ]
        self.assertEqual(
            Counter(park_identifiers), Counter(expected_identifiers),
            msg="Expects all identifiers to be present in park identifiers list.",
        )

        # Sequence index 1
        park_identifiers: List[IQubitID] = [element.identifier for element in sequence.get_gate_sequence_at_index(1).park_operations]
        expected_identifiers: List[IQubitID] = [
            QubitIDObj('X3'),
            QubitIDObj('Z4'),
            QubitIDObj('X2'),
        ]
        self.assertEqual(
            Counter(park_identifiers), Counter(expected_identifiers),
            msg="Expects all identifiers to be present in park identifiers list.",
        )

        # Sequence index 2
        park_identifiers: List[IQubitID] = [element.identifier for element in sequence.get_gate_sequence_at_index(2).park_operations]
        expected_identifiers: List[IQubitID] = [
            QubitIDObj('X3'),
            QubitIDObj('Z1'),
            QubitIDObj('X2'),
        ]
        self.assertEqual(
            Counter(park_identifiers), Counter(expected_identifiers),
            msg="Expects all identifiers to be present in park identifiers list.",
        )

        # Sequence index 3
        park_identifiers: List[IQubitID] = [element.identifier for element in sequence.get_gate_sequence_at_index(3).park_operations]
        expected_identifiers: List[IQubitID] = [
            QubitIDObj('X2'),
            QubitIDObj('Z2'),
        ]
        self.assertEqual(
            Counter(park_identifiers), Counter(expected_identifiers),
            msg="Expects all identifiers to be present in park identifiers list.",
        )

    def test_example_repetition_code_z4z2(self):
        """Tests specific repetition-code (distance-3) Z4-Z2."""
        circuit_description = RepetitionCodeDescription.from_connectivity(
            involved_qubit_ids=[QubitIDObj('D5'), QubitIDObj('Z4'), QubitIDObj('D6'), QubitIDObj('Z2'), QubitIDObj('D3')],
            connectivity=self.layout,
        )
        sequence: IGenericSurfaceCodeLayer = circuit_description.to_sequence()

        # Sequence index 0
        park_identifiers: List[IQubitID] = [element.identifier for element in sequence.get_gate_sequence_at_index(0).park_operations]
        expected_identifiers: List[IQubitID] = [
            QubitIDObj('Z4'),
            QubitIDObj('X2'),
        ]
        self.assertEqual(
            Counter(park_identifiers), Counter(expected_identifiers),
            msg="Expects all identifiers to be present in park identifiers list.",
        )

        # Sequence index 1
        park_identifiers: List[IQubitID] = [element.identifier for element in sequence.get_gate_sequence_at_index(1).park_operations]
        expected_identifiers: List[IQubitID] = [
        ]
        self.assertEqual(
            Counter(park_identifiers), Counter(expected_identifiers),
            msg="Expects all identifiers to be present in park identifiers list.",
        )

        # Sequence index 2
        park_identifiers: List[IQubitID] = [element.identifier for element in sequence.get_gate_sequence_at_index(2).park_operations]
        expected_identifiers: List[IQubitID] = [
            QubitIDObj('X3'),
            QubitIDObj('Z1'),
            QubitIDObj('X2'),
        ]
        self.assertEqual(
            Counter(park_identifiers), Counter(expected_identifiers),
            msg="Expects all identifiers to be present in park identifiers list.",
        )

        # Sequence index 3
        park_identifiers: List[IQubitID] = [element.identifier for element in sequence.get_gate_sequence_at_index(3).park_operations]
        expected_identifiers: List[IQubitID] = [
            QubitIDObj('X2'),
            QubitIDObj('Z2'),
        ]
        self.assertEqual(
            Counter(park_identifiers), Counter(expected_identifiers),
            msg="Expects all identifiers to be present in park identifiers list.",
        )
    # endregion

    # region Teardown
    @classmethod
    def tearDownClass(cls) -> None:
        """Closes any left over processes after testing"""
        pass
    # endregion
