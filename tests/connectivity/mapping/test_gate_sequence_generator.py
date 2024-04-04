import unittest
from qce_circuit.connectivity.mapping.gate_sequence_generator import (
    GateSequenceGenerator,
    GateSequenceIdentifier,
)
from qce_circuit.connectivity.connectivity_surface_code import Surface17Layer
from qce_circuit.connectivity.intrf_channel_identifier import EdgeIDObj, QubitIDObj
from qce_circuit.connectivity.generic_gate_sequence import IGenericSurfaceCodeLayer


class BasicSequenceGenerationTestCase(unittest.TestCase):

    # region Setup
    @classmethod
    def setUpClass(cls) -> None:
        """Set up for all test cases"""
        cls.connectivity = Surface17Layer()

    def setUp(self) -> None:
        """Set up for every test case"""
        pass
    # endregion

    # region Test Cases
    def test_simple_sequence_generation(self):
        """Tests sequence generation consisting of 8 gates in Surface-17 layout."""
        sequence_generator = GateSequenceGenerator(
            included_edge_ids=[
                EdgeIDObj(QubitIDObj('D5'), QubitIDObj('Z1')),
                EdgeIDObj(QubitIDObj('Z1'), QubitIDObj('D1')),
                EdgeIDObj(QubitIDObj('D1'), QubitIDObj('X1')),
                EdgeIDObj(QubitIDObj('X1'), QubitIDObj('D2')),
                EdgeIDObj(QubitIDObj('D2'), QubitIDObj('X2')),
                EdgeIDObj(QubitIDObj('X2'), QubitIDObj('D3')),
                EdgeIDObj(QubitIDObj('D3'), QubitIDObj('Z2')),
                EdgeIDObj(QubitIDObj('Z2'), QubitIDObj('D6')),
            ],
            connectivity=self.connectivity,
        )
        nr_elements: int = len(sequence_generator.included_edge_ids)
        group_size: int = 2
        nr_expected_combinations: int = 105
        self.assertEqual(
            GateSequenceGenerator.get_combination_size(nr_elements=nr_elements, group_size=group_size),
            nr_expected_combinations,
            msg=f"Expects {nr_expected_combinations} number of combinations."
        )
        sequence_identifier: GateSequenceIdentifier = sequence_generator.construct_allowed_gate_sequences(
            subgroup_size=group_size,
        )
        operation_sequence = sequence_identifier.construct_minimal_parking_sequence(connectivity=self.connectivity)
        nr_expected_unique_parkings: int = 6
        self.assertEqual(
            operation_sequence.get_unique_parking_count(connectivity=self.connectivity),
            nr_expected_unique_parkings,
        )
        generic_surface: IGenericSurfaceCodeLayer = operation_sequence.to_generic_surface_code(connectivity=self.connectivity)
        self.assertIsInstance(
            generic_surface,
            IGenericSurfaceCodeLayer,
        )
    # endregion

    # region Teardown
    @classmethod
    def tearDownClass(cls) -> None:
        """Closes any left over processes after testing"""
        pass
    # endregion
