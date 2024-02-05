import unittest
from typing import Dict
from qce_circuit.visualization.display_circuit import plot_circuit
from qce_circuit.library.repetition_code_circuit import (
    construct_repetition_code_circuit_simplified,
    InitialStateContainer,
    InitialStateEnum,
)
import matplotlib.pyplot as plt


class CustomChannelMapTestCase(unittest.TestCase):

    # region Setup
    @classmethod
    def setUpClass(cls) -> None:
        """Set up for all test cases"""
        initial_state: InitialStateContainer = InitialStateContainer.from_ordered_list([
            InitialStateEnum.ZERO,
            InitialStateEnum.ONE,
            InitialStateEnum.ZERO,
        ])
        cls.circuit = construct_repetition_code_circuit_simplified(
            initial_state=initial_state,
            qec_cycles=6,
        )

    def setUp(self) -> None:
        """Set up for every test case"""
        pass
    # endregion

    # region Test Cases
    def test_default_no_channel_map(self):
        """Tests default plotting function."""
        plot_circuit(self.circuit)
        self.assertTrue(True)

    def test_in_range_channel_map(self):
        """Tests default True."""
        channel_map: Dict[int, str] = {
            0: 'A',
            1: 'B',
            2: 'C',
            3: 'D',
            4: 'E',
        }
        plot_circuit(self.circuit, channel_map=channel_map)
        self.assertTrue(True)

    def test_out_of_range_channel_map(self):
        """Tests default True."""
        channel_map: Dict[int, str] = {
            00: 'A',
            -1: 'B',
            200: 'C',
            3: 'D',
            4: 'E',
        }
        plot_circuit(self.circuit, channel_map=channel_map)
        self.assertTrue(True)
    # endregion

    # region Teardown
    @classmethod
    def tearDownClass(cls) -> None:
        """Closes any left over processes after testing"""
        plt.close('all')
    # endregion
