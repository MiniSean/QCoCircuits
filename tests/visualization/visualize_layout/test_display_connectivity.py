import unittest
from qce_circuit.visualization.visualize_layout.display_connectivity import (
    VisualConnectivityDescription,
    plot_layout_description,
)
from qce_circuit.connectivity.connectivity_surface_code import Surface17Layer
import matplotlib.pyplot as plt


class DisplayConnectivityTestCase(unittest.TestCase):

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
    def test_default_visualization(self):
        """Tests if default plotting tool works."""
        layout = Surface17Layer()
        descriptor: VisualConnectivityDescription = VisualConnectivityDescription(
            connectivity=layout,
            layout_spacing=1.0
        )
        plot_layout_description(descriptor)
        self.assertTrue(True)
    # endregion

    # region Teardown
    @classmethod
    def tearDownClass(cls) -> None:
        """Closes any left over processes after testing"""
        plt.close('all')
    # endregion
