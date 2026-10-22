import unittest
from qce_circuit.connectivity.intrf_channel_identifier import QubitIDObj
from qce_circuit.connectivity.connectivity_dynamic_surface_code import DynamicSurfaceCodeLayer
from qce_circuit.library.surface_code.surface_code_connectivity import Surface17Round4Code
from qce_circuit.connectivity.generic_gate_sequence import TranslatedGenericSurfaceCodeLayer
from qce_circuit.utilities.custom_exceptions import LayoutTranslationException
from qce_circuit.utilities.geometric_definitions.vector_elements import Vec2D


class DynamicSurfaceCodeTestCase(unittest.TestCase):

    # region Setup
    @classmethod
    def setUpClass(cls) -> None:
        """Set up for all test cases."""
        pass

    def setUp(self) -> None:
        """Set up for every test case."""
        self.dynamic_3x3 = DynamicSurfaceCodeLayer(width=3, height=3)
        self.base_surface17 = Surface17Round4Code()
    # endregion

    # region Test Cases
    def test_dynamic_surface_code_layer_3x3_geometry(self) -> None:
        """Tests qubit and parity group composition for a 3x3 DynamicSurfaceCodeLayer."""
        self.assertEqual(len(self.dynamic_3x3.data_qubit_ids), 9)
        self.assertEqual(len(self.dynamic_3x3.ancilla_qubit_ids), 8)
        self.assertEqual(len(self.dynamic_3x3.qubit_ids), 17)
        self.assertEqual(len(self.dynamic_3x3.parity_group_x), 4)
        self.assertEqual(len(self.dynamic_3x3.parity_group_z), 4)

        # Coordinate extraction
        center_qubit = QubitIDObj('D4')
        coords: Vec2D = self.dynamic_3x3.get_qubit_coordinates(center_qubit)
        self.assertEqual(coords, Vec2D(0.0, 0.0))

        # Neighborhood and containment
        neighbors = self.dynamic_3x3.get_neighbors(center_qubit)
        self.assertGreater(len(neighbors), 0)
        self.assertTrue(self.dynamic_3x3.contains(center_qubit))

    def test_dynamic_surface_code_layer_rectangular(self) -> None:
        """Tests constructing a non-square rectangular DynamicSurfaceCodeLayer (4x3)."""
        layer_4x3 = DynamicSurfaceCodeLayer(width=4, height=3)
        self.assertEqual(len(layer_4x3.data_qubit_ids), 12)
        self.assertGreater(len(layer_4x3.ancilla_qubit_ids), 0)
        self.assertGreater(len(layer_4x3.edge_ids), 0)

    def test_translated_surface_code_layer_success(self) -> None:
        """Tests translating Surface17Round4Code onto a DynamicSurfaceCodeLayer matching anchors."""
        base_anchor = QubitIDObj('D5')
        target_anchor = QubitIDObj('D4')

        translated = TranslatedGenericSurfaceCodeLayer(
            base_layer=self.base_surface17,
            target_layer=self.dynamic_3x3,
            base_anchor=base_anchor,
            target_anchor=target_anchor,
        )

        self.assertEqual(len(translated.gate_sequences), 4)
        self.assertEqual(len(translated.parity_group_x), 4)
        self.assertEqual(len(translated.parity_group_z), 4)
        self.assertEqual(translated._qubit_mapping[base_anchor], target_anchor)

    def test_translated_surface_code_layer_out_of_bounds_raises(self) -> None:
        """Tests that translating outside target layer boundaries raises LayoutTranslationException."""
        base_anchor = QubitIDObj('D5')
        # Setting target anchor to boundary qubit D0 will push opposite side outside bounds
        target_anchor = QubitIDObj('D0')

        with self.assertRaises(LayoutTranslationException):
            TranslatedGenericSurfaceCodeLayer(
                base_layer=self.base_surface17,
                target_layer=self.dynamic_3x3,
                base_anchor=base_anchor,
                target_anchor=target_anchor,
            )
    # endregion

    # region Teardown
    @classmethod
    def tearDownClass(cls) -> None:
        """Closes any left over processes after testing."""
        pass
    # endregion


if __name__ == '__main__':
    unittest.main()
