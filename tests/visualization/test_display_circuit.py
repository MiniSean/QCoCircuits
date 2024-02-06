import unittest
from typing import Dict
from qce_circuit.visualization.display_circuit import plot_circuit
from qce_circuit.library.repetition_code_circuit import (
    construct_repetition_code_circuit_simplified,
    InitialStateContainer,
    InitialStateEnum,
)
from qce_circuit.language.declarative_circuit import DeclarativeCircuit
from qce_circuit.structure.circuit_operations import (
    CPhase,
    VirtualPark,
    Barrier,
    Identity,
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

    def test_follows_channel_order(self):
        """Tests default True."""
        channel_order = [1, 0, 2, 3, 4]
        channel_map: Dict[int, str] = {
            0: 'A',
            1: 'B',
            2: 'C',
            3: 'D',
            4: 'E',
        }
        plot_circuit(self.circuit, channel_order=channel_order, channel_map=channel_map)
        self.assertTrue(True)
    # endregion

    # region Teardown
    @classmethod
    def tearDownClass(cls) -> None:
        """Closes any left over processes after testing"""
        plt.close('all')
    # endregion


class DrawOperationsTestCase(unittest.TestCase):

    # region Setup
    @classmethod
    def setUpClass(cls) -> None:
        """Set up for all test cases"""
        pass

    def setUp(self) -> None:
        """Set up for every test case"""
        pass
    # endregion

    # region Test Cases
    def test_virtual_park(self):
        """Tests default True."""
        circuit = DeclarativeCircuit()
        circuit.add(Barrier([0, 1, 2]))
        circuit.add(CPhase(0, 2))
        circuit.add(VirtualPark(1))
        circuit.add(Barrier([0, 1, 2]))
        plot_circuit(circuit)

        self.assertTrue(True)
    # endregion

    # region Teardown
    @classmethod
    def tearDownClass(cls) -> None:
        """Closes any left over processes after testing"""
        plt.close('all')
    # endregion