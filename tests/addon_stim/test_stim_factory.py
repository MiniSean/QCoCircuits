import unittest
import stim
from qce_circuit.connectivity.intrf_channel_identifier import QubitIDObj
from qce_circuit.library.repetition_code.circuit_components import RepetitionCodeDescription
from qce_circuit.library.repetition_code.circuit_constructors import (
    construct_repetition_code_circuit,
)
from qce_circuit.library.repetition_code.repetition_code_connectivity import Repetition9Code
from qce_circuit.language import (
    InitialStateContainer,
    InitialStateEnum,
)
from qce_circuit.addon_stim import to_stim


class StimFactoryRepCodeTestCase(unittest.TestCase):

    # region Setup
    @classmethod
    def setUpClass(cls) -> None:
        """Set up for all test cases"""
        cls.initial_state: InitialStateContainer = InitialStateContainer.from_ordered_list([
            InitialStateEnum.ZERO,
            InitialStateEnum.ONE,
            InitialStateEnum.ZERO,
        ])
        cls.circuit = construct_repetition_code_circuit(
            description=RepetitionCodeDescription.from_initial_state(cls.initial_state),
            initial_state=cls.initial_state,
            qec_cycles=1,
        )
        cls.stim_circuit = to_stim(circuit=cls.circuit)

    def setUp(self) -> None:
        """Set up for every test case"""
        pass
    # endregion

    # region Test Cases
    def test_construction_specific_representation(self):
        """Tests circuit representation to expected value."""
        # Create specific repetition circuit based on Surface-17 layout
        circuit_description: RepetitionCodeDescription = RepetitionCodeDescription.from_connectivity(
            involved_qubit_ids=[
                QubitIDObj('D4'),
                QubitIDObj('Z1'),
                QubitIDObj('D5'),
                QubitIDObj('Z4'),
                QubitIDObj('D6'),
            ],
            connectivity=Repetition9Code(),
        )
        circuit = construct_repetition_code_circuit(
            description=circuit_description,
            initial_state=self.initial_state,
            qec_cycles=1,
        )
        stim_circuit = to_stim(circuit=circuit)

        expected_repr: str = '''
            R 0 1 2 3 4
            M 0 1 2 3 4
            TICK
            I 0
            X 2
            I 4
            TICK
            SQRT_Y 1
            TICK
            CZ 1 0
            TICK
            TICK
            CZ 1 2
            TICK
            TICK
            SQRT_Y_DAG 1
            SQRT_Y 3
            TICK
            CZ 3 2
            TICK
            TICK
            CZ 3 4
            TICK
            TICK
            SQRT_Y_DAG 3
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
            stim_circuit,
            msg="Expected circuit result"
        )

    def test_construction_arbitrary_length_representation(self):
        """Tests circuit representation to expected value."""

        expected_repr: str = '''
            R 0 1 2 3 4
            M 0 1 2 3 4
            TICK
            I 0
            X 2
            I 4
            TICK
            SQRT_Y 1 3
            TICK
            CZ 0 1 2 3
            TICK
            TICK
            CZ 1 2 3 4
            TICK
            TICK
            SQRT_Y_DAG 1 3
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

    def test_construction_zero_qec_rounds(self):
        """Tests circuit representation to 0 qec-cycles."""
        # Create specific repetition circuit based on Surface-17 layout
        circuit_description: RepetitionCodeDescription = RepetitionCodeDescription.from_connectivity(
            involved_qubit_ids=[
                QubitIDObj('D6'),
                QubitIDObj('Z2'),
                QubitIDObj('D3'),
                QubitIDObj('X2'),
                QubitIDObj('D2'),
            ],
            connectivity=Repetition9Code(),
        )
        circuit = construct_repetition_code_circuit(
            description=circuit_description,
            initial_state=self.initial_state,
            qec_cycles=0,
        )
        stim_circuit = to_stim(circuit=circuit)

        expected_repr: str = '''
            R 0 1 2 3 4
            M 0 1 2 3 4
            TICK
            I 0
            X 2
            I 4
            TICK
            M 0 2 4
            DETECTOR(1, 0) rec[-3] rec[-2]
            DETECTOR(3, 0) rec[-1] rec[-2]
            OBSERVABLE_INCLUDE(0) rec[-3]
            OBSERVABLE_INCLUDE(0) rec[-2]
            OBSERVABLE_INCLUDE(0) rec[-1]
        '''
        self.assertEqual(
            stim.Circuit(expected_repr),
            stim_circuit,
            msg="Expected circuit result"
        )
    # endregion

    # region Teardown
    @classmethod
    def tearDownClass(cls) -> None:
        """Closes any left over processes after testing"""
        pass
    # endregion
