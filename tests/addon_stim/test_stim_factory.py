import unittest
import stim
from qce_circuit.library.repetition_code.repetition_code_circuit import (
    InitialStateContainer,
    InitialStateEnum,
    construct_repetition_code_circuit,
)
from qce_circuit.addon_stim import to_stim


class StimFactoryRepCodeTestCase(unittest.TestCase):

    # region Setup
    @classmethod
    def setUpClass(cls) -> None:
        """Set up for all test cases"""
        initial_state: InitialStateContainer = InitialStateContainer.from_ordered_list([
            InitialStateEnum.ZERO,
            InitialStateEnum.ONE,
            InitialStateEnum.ZERO,
        ])
        cls.circuit = construct_repetition_code_circuit(
            initial_state=initial_state,
            qec_cycles=1,
        )
        cls.stim_circuit = to_stim(circuit=cls.circuit)

    def setUp(self) -> None:
        """Set up for every test case"""
        pass
    # endregion

    # region Test Cases
    def test_construction_representation(self):
        """Tests circuit representation to expected value."""
        expected_repr: str = '''
            R 0 1 2 3 4
            M 0 1 2 3 4
            TICK
            I 0
            X 2
            I 4
            TICK
            H 1
            TICK
            CZ 0 1
            TICK
            CZ 1 2
            TICK
            H 1 3
            TICK
            CZ 2 3
            TICK
            CZ 3 4
            TICK
            H 3
            TICK
            M 1 3
            DETECTOR(1, 0) rec[-2]
            DETECTOR(3, 0) rec[-1]
            SHIFT_COORDS(0, 1)
            M 0 2 4
            DETECTOR(1, 0) rec[-3] rec[-2] rec[-5]
            DETECTOR(3, 0) rec[-2] rec[-1] rec[-4]
            OBSERVABLE_INCLUDE(0) rec[-3]
            OBSERVABLE_INCLUDE(0) rec[-2]
            OBSERVABLE_INCLUDE(0) rec[-1]
        '''
        self.assertEqual(
            stim.Circuit(expected_repr),
            self.stim_circuit,
            msg="Expected circuit result"
        )

    # endregion

    # region Teardown
    @classmethod
    def tearDownClass(cls) -> None:
        """Closes any left over processes after testing"""
        pass
    # endregion
