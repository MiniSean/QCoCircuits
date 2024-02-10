import unittest
from qce_circuit.visualization.visualize_layout.display_connectivity import (
    VisualConnectivityDescription,
    plot_layout_description,
    plot_gate_sequences,
)
from qce_circuit.connectivity.intrf_channel_identifier import QubitIDObj
from qce_circuit.connectivity.connectivity_surface_code import Surface17Layer
from qce_circuit.connectivity.intrf_connectivity_gate_sequence import GateSequenceLayer
from qce_circuit.visualization.visualize_layout.element_components import TextComponent
from qce_circuit.utilities.geometric_definitions.intrf_rectilinear_transform import TransformAlignment
from qce_circuit.library.repetition_code_connectivity import Repetition9Code
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

    def test_text_visualization(self):
        """Tests (element) text plotting."""
        layout = Surface17Layer()
        descriptor: VisualConnectivityDescription = VisualConnectivityDescription(
            connectivity=layout,
            gate_sequence=GateSequenceLayer.empty(),
            layout_spacing=1.0
        )
        fig, ax = plot_layout_description(
            description=descriptor,
        )
        # Draw text component
        component: TextComponent = TextComponent(
            pivot=descriptor.identifier_to_pivot(QubitIDObj('D6')),
            text='D6',
            alignment=TransformAlignment.MID_CENTER,
        )
        component.draw(axes=ax)

        component: TextComponent = TextComponent(
            pivot=descriptor.identifier_to_pivot(QubitIDObj('D5')),
            text='A',
            color='r',
            alignment=TransformAlignment.MID_CENTER,
        )
        component.draw(axes=ax)

        component: TextComponent = TextComponent(
            pivot=descriptor.identifier_to_pivot(QubitIDObj('D4')),
            text=r'$| \Psi \rangle$',
            alignment=TransformAlignment.MID_CENTER,
        )
        component.draw(axes=ax)
        self.assertTrue(True)

    def test_full_repetition_code_visualization(self):
        """Tests visualization of full repetition code gate sequence."""
        plot_gate_sequences(
            description=Repetition9Code()
        )
        self.assertTrue(True)
    # endregion

    # region Teardown
    @classmethod
    def tearDownClass(cls) -> None:
        """Closes any left over processes after testing"""
        plt.close('all')
    # endregion
