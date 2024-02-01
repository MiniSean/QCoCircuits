# -------------------------------------------
# Module containing visualization for ISurfaceCodeLayer.
# -------------------------------------------
from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np

from qce_circuit.connectivity.intrf_connectivity_surface_code import ISurfaceCodeLayer
from qce_circuit.connectivity.intrf_channel_identifier import IQubitID, QubitIDObj
from qce_circuit.utilities.geometric_definitions import (
    TransformAlignment,
    Vec2D,
)
from qce_circuit.visualization.intrf_draw_component import IDrawComponent
from qce_circuit.visualization.visualize_layout.plaquette_components import (
    RectanglePlaquette,
    TrianglePlaquette,
)
from qce_circuit.visualization.visualize_layout.element_components import (
    DotComponent
)
from qce_circuit.visualization.plotting_functionality import (
    construct_subplot,
    SubplotKeywordEnum,
    IAxesFormat,
    AxesFormat,
    LabelFormat,
    IFigureAxesPair,
)


@dataclass(frozen=True)
class VisualConnectivityDescription:
    """
    Data class, containing all information required to draw circuit.
    Implements basic visualization.
    """
    connectivity: ISurfaceCodeLayer
    layout_spacing: float = field(default=1)
    rotation: float = field(default=45)

    # region Class Methods
    def get_plaquette_components(self) -> List[IDrawComponent]:
        result: List[IDrawComponent] = []
        for parity_group in self.connectivity.parity_group_x:
            if len(parity_group.data_ids) == 4:
                result.append(
                    RectanglePlaquette(
                        pivot=self.identifier_to_pivot(parity_group.ancilla_id),
                        width=self.layout_spacing,
                        height=self.layout_spacing,
                        alignment=TransformAlignment.MID_CENTER,
                    )
                )
            if len(parity_group.data_ids) == 2:
                result.append(
                    TrianglePlaquette(
                        pivot=self.identifier_to_pivot(parity_group.ancilla_id),
                        width=self.layout_spacing,
                        height=self.layout_spacing,
                        rotation=90,
                        alignment=TransformAlignment.MID_CENTER,
                    )
                )
        return result

    def get_element_components(self) -> List[IDrawComponent]:
        return [
            DotComponent(
                pivot=self.identifier_to_pivot(qubit_id),
                alignment=TransformAlignment.MID_CENTER,
            )
            for qubit_id in self.connectivity.qubit_ids
        ]

    def identifier_to_pivot(self, identifier: IQubitID) -> Vec2D:
        """:return: Pivot based on channel identifier and duration component."""
        # Surface-17 layout
        map_qubits: Dict[IQubitID, Vec2D] = {
            QubitIDObj('Z3'): Vec2D(-2, -1) * self.layout_spacing,
            QubitIDObj('D9'): Vec2D(0, 2) * self.layout_spacing,
            QubitIDObj('X4'): Vec2D(-1, 2) * self.layout_spacing,
            QubitIDObj('D8'): Vec2D(-1, 1) * self.layout_spacing,
            QubitIDObj('Z4'): Vec2D(0, 1) * self.layout_spacing,
            QubitIDObj('D6'): Vec2D(1, 1) * self.layout_spacing,
            QubitIDObj('D7'): Vec2D(-2, 0) * self.layout_spacing,
            QubitIDObj('X3'): Vec2D(-1, 0) * self.layout_spacing,
            QubitIDObj('D5'): Vec2D(0, 0) * self.layout_spacing,
            QubitIDObj('X2'): Vec2D(1, 0) * self.layout_spacing,
            QubitIDObj('D3'): Vec2D(2, 0) * self.layout_spacing,
            QubitIDObj('D4'): Vec2D(-1, -1) * self.layout_spacing,
            QubitIDObj('Z1'): Vec2D(0, -1) * self.layout_spacing,
            QubitIDObj('D2'): Vec2D(1, -1) * self.layout_spacing,
            QubitIDObj('X1'): Vec2D(1, -2) * self.layout_spacing,
            QubitIDObj('Z2'): Vec2D(2, 1) * self.layout_spacing,
            QubitIDObj('D1'): Vec2D(0, -2) * self.layout_spacing,
        }
        if identifier in map_qubits:
            return map_qubits[identifier].rotate(np.deg2rad(self.rotation))
        return (Vec2D(0, 0) * self.layout_spacing).rotate(np.deg2rad(self.rotation))  # Default
    # endregion


def plot_layout_description(description: VisualConnectivityDescription, **kwargs) -> IFigureAxesPair:
    # Data allocation
    # kwargs[SubplotKeywordEnum.AXES_FORMAT.value] = CircuitAxesFormat()
    kwargs[SubplotKeywordEnum.LABEL_FORMAT.value] = LabelFormat(x_label='', y_label='')
    fig, ax = construct_subplot(**kwargs)

    for draw_component in description.get_plaquette_components():
        draw_component.draw(axes=ax)

    for draw_component in description.get_element_components():
        draw_component.draw(axes=ax)

    ax.set_aspect('equal')
    ax.set_xlim([-3, 3])
    ax.set_ylim([-3, 3])
    return fig, ax


if __name__ == '__main__':
    from qce_circuit.connectivity.connectivity_surface_code import Surface17Layer
    from qce_circuit.connectivity.connectivity_repetition_code import Repetition9Layer
    import matplotlib.pyplot as plt

    layout = Surface17Layer()
    descriptor: VisualConnectivityDescription = VisualConnectivityDescription(
        connectivity=layout,
        layout_spacing=1.0
    )
    print(descriptor.get_plaquette_components())
    plot_layout_description(descriptor)

    plt.show()
