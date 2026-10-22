import unittest
from qce_circuit.connectivity.intrf_channel_identifier import QubitIDObj
from qce_circuit.connectivity.intrf_connectivity_surface_code import StabilizerType
from qce_circuit.library.repetition_code.repetition_code_connectivity import (
    Repetition9Round2Code,
    Repetition9Round2XCode,
)


class RepetitionCodeXTestCase(unittest.TestCase):

    # region Setup
    @classmethod
    def setUpClass(cls) -> None:
        """Set up for all test cases."""
        pass

    def setUp(self) -> None:
        """Set up for every test case."""
        self.code_z = Repetition9Round2Code()
        self.code_x = Repetition9Round2XCode()
    # endregion

    # region Test Cases
    def test_singleton_instances(self) -> None:
        """Tests that Repetition9Round2XCode behaves as a singleton instance."""
        instance1 = Repetition9Round2XCode()
        instance2 = Repetition9Round2XCode()
        self.assertIs(instance1, instance2)

    def test_qubit_composition(self) -> None:
        """Tests that Repetition9Round2XCode has 9 data qubits and 8 ancillas."""
        self.assertEqual(len(self.code_x.data_qubit_ids), 9)
        self.assertEqual(len(self.code_x.ancilla_qubit_ids), 8)
        self.assertEqual(len(self.code_x.qubit_ids), 17)

        # Expected data qubits D1..D9
        for i in range(1, 10):
            self.assertIn(QubitIDObj(f'D{i}'), self.code_x.data_qubit_ids)

    def test_gate_sequence_structure(self) -> None:
        """Tests that Repetition9Round2XCode has 2 gate sequences with 8 two-qubit gates each."""
        self.assertEqual(self.code_x.gate_sequence_count, 2)
        seq0 = self.code_x.get_gate_sequence_at_index(0)
        seq1 = self.code_x.get_gate_sequence_at_index(1)

        self.assertEqual(len(seq0.gate_operations), 8)
        self.assertEqual(len(seq1.gate_operations), 8)

    def test_x_basis_parity_groups(self) -> None:
        """Tests that Repetition9Round2XCode exclusively defines X-type parity groups."""
        self.assertEqual(len(self.code_x.parity_group_z), 0)
        self.assertEqual(len(self.code_x.parity_group_x), 8)

        for pg in self.code_x.parity_group_x:
            self.assertEqual(pg.parity_type, StabilizerType.STABILIZER_X)
            self.assertEqual(len(pg.data_ids), 2)
            for data_id in pg.data_ids:
                self.assertEqual(pg.get_stabilizer_type(data_id), StabilizerType.STABILIZER_X)

    def test_contrast_with_z_basis_repetition_code(self) -> None:
        """Tests orthogonal parity basis between X-type and standard Z-type repetition codes."""
        # Z-code has all in parity_group_z, 0 in parity_group_x
        self.assertEqual(len(self.code_z.parity_group_z), 8)
        self.assertEqual(len(self.code_z.parity_group_x), 0)

        # X-code has all in parity_group_x, 0 in parity_group_z
        self.assertEqual(len(self.code_x.parity_group_z), 0)
        self.assertEqual(len(self.code_x.parity_group_x), 8)
    # endregion

    # region Teardown
    @classmethod
    def tearDownClass(cls) -> None:
        """Closes any left over processes after testing."""
        pass
    # endregion


if __name__ == '__main__':
    unittest.main()
