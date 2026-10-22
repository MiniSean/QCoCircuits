import unittest
from typing import List
from qce_circuit.connectivity.intrf_channel_identifier import QubitIDObj, IQubitID
from qce_circuit.connectivity.intrf_connectivity_surface_code import StabilizerType, IParityGroup
from qce_circuit.library.surface_code.surface_code_connectivity import (
    Surface17Round4Code,
    Surface17Round4ZXXZCode,
    Surface17Round8BCode,
    Surface17Round8CCode,
    Surface13ARound4Code,
    Surface13CRound4Code,
)


class SurfaceCodeZXXZTestCase(unittest.TestCase):

    # region Setup
    @classmethod
    def setUpClass(cls) -> None:
        """Set up for all test cases."""
        pass

    def setUp(self) -> None:
        """Set up for every test case."""
        self.css_code = Surface17Round4Code()
        self.zxxz_code = Surface17Round4ZXXZCode()
    # endregion

    # region Test Cases
    def test_singleton_instances(self) -> None:
        """Tests singleton behavior for Surface17Round4ZXXZCode and CSS Surface17Round4Code."""
        instance1 = Surface17Round4ZXXZCode()
        instance2 = Surface17Round4ZXXZCode()
        self.assertIs(instance1, instance2)

    def test_zxxz_qubit_composition(self) -> None:
        """Tests that Surface17Round4ZXXZCode contains exactly 17 qubits (9 data, 8 ancillas)."""
        self.assertEqual(len(self.zxxz_code.qubit_ids), 17)
        self.assertEqual(len(self.zxxz_code.data_qubit_ids), 9)
        self.assertEqual(len(self.zxxz_code.ancilla_qubit_ids), 8)

        # Confirm data qubits are D1..D9
        expected_data_ids = [QubitIDObj(f'D{i}') for i in range(1, 10)]
        for data_id in expected_data_ids:
            self.assertIn(data_id, self.zxxz_code.data_qubit_ids)

    def test_zxxz_gate_sequences(self) -> None:
        """Tests that Surface17Round4ZXXZCode has 4 gate sequence layers with valid interactions."""
        self.assertEqual(self.zxxz_code.gate_sequence_count, 4)
        for seq_idx in range(self.zxxz_code.gate_sequence_count):
            seq = self.zxxz_code.get_gate_sequence_at_index(seq_idx)
            self.assertGreater(len(seq.gate_operations), 0)

    def test_zxxz_mixed_stabilizer_parity_groups(self) -> None:
        """
        Tests that weight-4 parity groups in Surface17Round4ZXXZCode contain mixed
        Z and X stabilizer types, distinguishing it from standard CSS Surface-17.
        """
        # In CSS Surface-17, parity group elements are uniform within a group
        for pg in self.css_code.parity_group_x:
            types = {pg.get_stabilizer_type(dq) for dq in pg.data_ids}
            self.assertEqual(types, {StabilizerType.STABILIZER_X})

        for pg in self.css_code.parity_group_z:
            types = {pg.get_stabilizer_type(dq) for dq in pg.data_ids}
            self.assertEqual(types, {StabilizerType.STABILIZER_Z})

        # In ZXXZ Surface-17, weight-4 ancillas must contain BOTH X and Z stabilizers
        weight_4_ancillas = [QubitIDObj('X2'), QubitIDObj('X3'), QubitIDObj('Z1'), QubitIDObj('Z4')]

        for ancilla_id in weight_4_ancillas:
            pg: IParityGroup = self.zxxz_code.get_parity_group(ancilla_id)[0]
            stabilizer_types = [pg.get_stabilizer_type(dq) for dq in pg.data_ids]

            self.assertEqual(len(stabilizer_types), 4)
            self.assertIn(StabilizerType.STABILIZER_X, stabilizer_types)
            self.assertIn(StabilizerType.STABILIZER_Z, stabilizer_types)
            # Count should be 2 X's and 2 Z's for ZXXZ
            self.assertEqual(stabilizer_types.count(StabilizerType.STABILIZER_X), 2)
            self.assertEqual(stabilizer_types.count(StabilizerType.STABILIZER_Z), 2)

    def test_additional_surface_code_variants(self) -> None:
        """Tests initialization and basic geometry of additional surface code variants."""
        code_8b = Surface17Round8BCode()
        code_8c = Surface17Round8CCode()
        code_13a = Surface13ARound4Code()
        code_13c = Surface13CRound4Code()

        self.assertEqual(code_8b.gate_sequence_count, 8)
        self.assertEqual(code_8c.gate_sequence_count, 8)
        self.assertEqual(len(code_13a.data_qubit_ids), 9)
        self.assertEqual(len(code_13a.ancilla_qubit_ids), 4)
        self.assertEqual(len(code_13c.data_qubit_ids), 9)
        self.assertEqual(len(code_13c.ancilla_qubit_ids), 4)
    # endregion

    # region Teardown
    @classmethod
    def tearDownClass(cls) -> None:
        """Closes any left over processes after testing."""
        pass
    # endregion


if __name__ == '__main__':
    unittest.main()
