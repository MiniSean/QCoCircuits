# -------------------------------------------
# Module containing visualization for ISurfaceCodeLayer.
# -------------------------------------------
from dataclasses import dataclass, field
from typing import Dict, List
import numpy as np
from qce_circuit.connectivity.intrf_channel_identifier import IQubitID, QubitIDObj
from qce_circuit.connectivity.intrf_connectivity_surface_code import ISurfaceCodeLayer
from qce_circuit.connectivity.connectivity_surface_code import Surface17Layer
from qce_circuit.connectivity.intrf_connectivity_gate_sequence import (
    IGateSequenceLayer,
    GateSequenceLayer,
)
from qce_circuit.connectivity.generic_gate_sequence import IGenericSurfaceCodeLayer
from qce_circuit.utilities.geometric_definitions import (
    TransformAlignment,
    Vec2D,
)
from qce_circuit.visualization.intrf_draw_component import IDrawComponent
from qce_circuit.visualization.visualize_layout.style_manager import StyleManager
from qce_circuit.visualization.visualize_layout.plaquette_components import (
    RectanglePlaquette,
    TrianglePlaquette,
)
from qce_circuit.visualization.visualize_layout.element_components import (
    DotComponent,
    HexagonComponent,
    ParkingComponent,
)
from qce_circuit.visualization.visualize_layout.polygon_component import (
    PolylineComponent,
    GateOperationComponent,
)
from qce_circuit.visualization.display_circuit import CircuitAxesFormat
from qce_circuit.visualization.plotting_functionality import (
    construct_subplot,
    SubplotKeywordEnum,
    LabelFormat,
    IFigureAxesPair,
)


@dataclass(frozen=True)
class SequenceFrame:
    """
    Data class, containing connectivity, gates and parking identifiers for a single sequence 'frame'.
    """
    pass


@dataclass(frozen=True)
class VisualConnectivityDescription:
    """
    Data class, containing all information required to draw circuit.
    Implements basic visualization.
    """
    connectivity: ISurfaceCodeLayer
    gate_sequence: GateSequenceLayer
    layout_spacing: float = field(default=1.0)
    pivot: Vec2D = field(default=Vec2D(0, 0))
    rotation: float = field(default=-45)

    # region Class Methods
    def get_plaquette_components(self) -> List[IDrawComponent]:
        result: List[IDrawComponent] = []
        diagonal_spacing: float = self.layout_spacing * np.sqrt(2)

        for parity_group in self.connectivity.parity_group_x:
            if len(parity_group.data_ids) == 4:
                result.append(
                    RectanglePlaquette(
                        pivot=self.identifier_to_pivot(parity_group.ancilla_id) + self.pivot,
                        width=diagonal_spacing,
                        height=diagonal_spacing,
                        rotation=self.identifier_to_rotation(parity_group.ancilla_id),
                        alignment=TransformAlignment.MID_CENTER,
                        style_settings=StyleManager.read_config().plaquette_style_x,
                    )
                )
            if len(parity_group.data_ids) == 2:
                result.append(
                    TrianglePlaquette(
                        pivot=self.identifier_to_pivot(parity_group.ancilla_id) + self.pivot,
                        width=diagonal_spacing,
                        height=diagonal_spacing,
                        rotation=self.identifier_to_rotation(parity_group.ancilla_id),
                        alignment=TransformAlignment.MID_CENTER,
                        style_settings=StyleManager.read_config().plaquette_style_x,
                    )
                )
        for parity_group in self.connectivity.parity_group_z:
            if len(parity_group.data_ids) == 4:
                result.append(
                    RectanglePlaquette(
                        pivot=self.identifier_to_pivot(parity_group.ancilla_id) + self.pivot,
                        width=diagonal_spacing,
                        height=diagonal_spacing,
                        rotation=self.identifier_to_rotation(parity_group.ancilla_id),
                        alignment=TransformAlignment.MID_CENTER,
                        style_settings=StyleManager.read_config().plaquette_style_z,
                    )
                )
            if len(parity_group.data_ids) == 2:
                result.append(
                    TrianglePlaquette(
                        pivot=self.identifier_to_pivot(parity_group.ancilla_id) + self.pivot,
                        width=diagonal_spacing,
                        height=diagonal_spacing,
                        rotation=self.identifier_to_rotation(parity_group.ancilla_id),
                        alignment=TransformAlignment.MID_CENTER,
                        style_settings=StyleManager.read_config().plaquette_style_z,
                    )
                )
        return result

    def get_element_components(self) -> List[IDrawComponent]:
        return [
            # HexagonComponent(
            #     rotation=self.identifier_to_rotation(qubit_id),
            #     pivot=self.identifier_to_pivot(qubit_id) + self.pivot,
            #     alignment=TransformAlignment.MID_CENTER,
            # )
            DotComponent(
                pivot=self.identifier_to_pivot(qubit_id) + self.pivot,
                alignment=TransformAlignment.MID_CENTER,
            )
            for qubit_id in self.connectivity.qubit_ids
        ]

    def get_line_components(self) -> List[IDrawComponent]:
        return [
            PolylineComponent(
                vertices=[
                    self.identifier_to_pivot(QubitIDObj('D7')),
                    self.identifier_to_pivot(QubitIDObj('Z3')),
                    self.identifier_to_pivot(QubitIDObj('D4')),
                    self.identifier_to_pivot(QubitIDObj('Z1')),
                    self.identifier_to_pivot(QubitIDObj('D5')),
                    self.identifier_to_pivot(QubitIDObj('Z4')),
                    self.identifier_to_pivot(QubitIDObj('D6')),
                    self.identifier_to_pivot(QubitIDObj('Z2')),
                    self.identifier_to_pivot(QubitIDObj('D3')),
                ],
            )
        ]

    def get_operation_components(self) -> List[IDrawComponent]:
        park_components: List[IDrawComponent] = [
            ParkingComponent(
                pivot=self.identifier_to_pivot(identifier=operation.identifier),
                alignment=TransformAlignment.MID_CENTER,
            )
            for operation in self.gate_sequence.park_operations
        ]
        gate_components: List[IDrawComponent] = [
            GateOperationComponent(
                pivot0=self.identifier_to_pivot(identifier=operation.identifier.qubit_ids[0]),
                pivot1=self.identifier_to_pivot(identifier=operation.identifier.qubit_ids[1]),
                alignment=TransformAlignment.MID_CENTER,
            )
            for operation in self.gate_sequence.gate_operations
        ]
        return park_components + gate_components

    def identifier_to_pivot(self, identifier: IQubitID) -> Vec2D:
        """:return: Pivot based on qubit identifier."""
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
            return map_qubits[identifier].rotate(np.deg2rad(self.rotation)) + self.pivot
        return self.pivot  # Default

    def identifier_to_rotation(self, identifier: IQubitID) -> float:
        """:return: Rotation based on (parity group) ancilla identifier."""
        rotation_offset: float = -45
        hexagon_rotation: float = 30

        # Surface-17 layout
        map_qubits: Dict[IQubitID, float] = {
            QubitIDObj('Z3'): self.rotation + rotation_offset + 0,
            QubitIDObj('X4'): self.rotation + rotation_offset + 270,
            QubitIDObj('Z4'): self.rotation + rotation_offset,
            QubitIDObj('X3'): self.rotation + rotation_offset,
            QubitIDObj('X2'): self.rotation + rotation_offset,
            QubitIDObj('Z1'): self.rotation + rotation_offset,
            QubitIDObj('X1'): self.rotation + rotation_offset + 90,
            QubitIDObj('Z2'): self.rotation + rotation_offset + 180,
            QubitIDObj('D1'): self.rotation + rotation_offset + hexagon_rotation,
            QubitIDObj('D2'): self.rotation + rotation_offset + hexagon_rotation,
            QubitIDObj('D3'): self.rotation + rotation_offset + hexagon_rotation,
            QubitIDObj('D4'): self.rotation + rotation_offset + hexagon_rotation,
            QubitIDObj('D5'): self.rotation + rotation_offset + hexagon_rotation,
            QubitIDObj('D6'): self.rotation + rotation_offset + hexagon_rotation,
            QubitIDObj('D7'): self.rotation + rotation_offset + hexagon_rotation,
            QubitIDObj('D8'): self.rotation + rotation_offset + hexagon_rotation,
            QubitIDObj('D9'): self.rotation + rotation_offset + hexagon_rotation,
        }
        if identifier in map_qubits:
            return map_qubits[identifier]
        return self.rotation  # default
    # endregion


def plot_layout_description(description: VisualConnectivityDescription, **kwargs) -> IFigureAxesPair:
    # Data allocation
    kwargs[SubplotKeywordEnum.FIGURE_SIZE.value] = kwargs.get(SubplotKeywordEnum.FIGURE_SIZE.value, (5, 5))
    kwargs[SubplotKeywordEnum.AXES_FORMAT.value] = kwargs.get(SubplotKeywordEnum.AXES_FORMAT.value, CircuitAxesFormat())
    kwargs[SubplotKeywordEnum.LABEL_FORMAT.value] = LabelFormat(x_label='', y_label='')
    fig, ax = construct_subplot(**kwargs)

    for draw_component in description.get_plaquette_components():
        draw_component.draw(axes=ax)

    for draw_component in description.get_element_components():
        draw_component.draw(axes=ax)

    for draw_component in description.get_operation_components():
        draw_component.draw(axes=ax)

    ax.set_aspect('equal')
    ax.set_xlim([-3, 3])
    ax.set_ylim([-3, 3])
    return fig, ax


def plot_gate_sequences(description: IGenericSurfaceCodeLayer, **kwargs) -> IFigureAxesPair:
    sequence_count: int = description.gate_sequence_count
    kwargs[SubplotKeywordEnum.FIGURE_SIZE.value] = (5 * sequence_count, 5)
    fig, axes = construct_subplot(ncols=sequence_count, **kwargs)

    for i, ax in enumerate(axes):
        descriptor: VisualConnectivityDescription = VisualConnectivityDescription(
            connectivity=Surface17Layer(),
            gate_sequence=description.get_gate_sequence_at_index(i),
            layout_spacing=1.0
        )
        kwargs[SubplotKeywordEnum.HOST_AXES.value] = (fig, ax)
        plot_layout_description(descriptor, **kwargs)
    return fig, axes[0]


if __name__ == '__main__':
    from qce_circuit.library.repetition_code_connectivity import Repetition9Code
    from qce_circuit.visualization.visualize_layout.element_components import TextComponent
    import matplotlib.pyplot as plt

    """
    Simplest case is provide:
    - Device layout,
    - (list) park qubit-ID's.
    - (list) gate edge-ID's.
    
    More complex case, provide:
    - Surface code -> sequence steps -> (list) simplest case.
    """

    descriptor: VisualConnectivityDescription = VisualConnectivityDescription(
        connectivity=Surface17Layer(),
        gate_sequence=Repetition9Code().get_gate_sequence_at_index(0),
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

    # plot_gate_sequences(
    #     description=Repetition9Code()
    # )
    plt.show()
