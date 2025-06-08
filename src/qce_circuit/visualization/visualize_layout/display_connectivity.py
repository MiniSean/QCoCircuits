# -------------------------------------------
# Module containing visualization for ISurfaceCodeLayer.
# -------------------------------------------
from dataclasses import dataclass, field
from collections.abc import Iterable
from typing import Dict, List, Union
import numpy as np
from qce_circuit.connectivity.intrf_channel_identifier import IQubitID, QubitIDObj
from qce_circuit.connectivity.intrf_connectivity_surface_code import ISurfaceCodeLayer, IParityGroup
from qce_circuit.connectivity.connectivity_surface_code import Surface17Layer
from qce_circuit.connectivity.intrf_connectivity_gate_sequence import (
    GateSequenceLayer,
)
from qce_circuit.connectivity.generic_gate_sequence import IGenericSurfaceCodeLayer
from qce_circuit.utilities.geometric_definitions import (
    TransformAlignment,
    Vec2D,
    Line2D,
)
from qce_circuit.visualization.visualize_circuit.intrf_draw_component import IDrawComponent
from qce_circuit.visualization.visualize_layout.style_manager import (
    StyleManager,
    PlaquetteStyleSettings,
    ElementStyleSettings,
    StyleSettings,
)
from qce_circuit.visualization.visualize_layout.plaquette_components import (
    RectanglePlaquette,
    TrianglePlaquette,
    DiagonalPlaquette,
)
from qce_circuit.visualization.visualize_layout.element_components import (
    DotComponent,
    ParkingComponent,
    TextComponent,
)
from qce_circuit.visualization.visualize_layout.polygon_component import (
    PolylineComponent,
    GateOperationComponent,
)
from qce_circuit.visualization.visualize_circuit.display_circuit import CircuitAxesFormat
from qce_circuit.visualization.visualize_circuit.plotting_functionality import (
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
    gate_sequence: GateSequenceLayer = field(default_factory=GateSequenceLayer.empty)
    layout_spacing: float = field(default=1.0)
    pivot: Vec2D = field(default=Vec2D(0, 0))
    rotation: float = field(default=-45)

    # region Class Methods
    def get_plaquette_components(self) -> List[IDrawComponent]:
        result: List[IDrawComponent] = []
        diagonal_spacing: float = self.layout_spacing * np.sqrt(2)

        for parity_group in self.connectivity.parity_group_x:
            ancilla_coordinates: Vec2D = self.identifier_to_pivot(identifier=parity_group.ancilla_id)
            relative_coordinates: List[Vec2D] = [
                self.identifier_to_pivot(identifier=qubit_id) - ancilla_coordinates
                for qubit_id in parity_group.data_ids
            ]
            mean_relative_coordinates: Vec2D = Vec2D(
                x=np.mean([v.x for v in relative_coordinates]),
                y=np.mean([v.y for v in relative_coordinates]),
            )
            mean_center: bool = all(np.isclose(mean_relative_coordinates.to_vector(), Vec2D(0.0, 0.0).to_vector()))

            if len(parity_group.data_ids) == 4:
                result.append(
                    RectanglePlaquette(
                        pivot=self.identifier_to_pivot(parity_group.ancilla_id) + self.pivot,
                        width=diagonal_spacing,
                        height=diagonal_spacing,
                        rotation=self.identifier_to_rotation(parity_group),
                        alignment=TransformAlignment.MID_CENTER,
                        style_settings=StyleManager.read_config().plaquette_style_x,
                    )
                )
            if len(parity_group.data_ids) == 2:
                if mean_center:
                    result.append(
                        DiagonalPlaquette(
                            pivot=self.identifier_to_pivot(parity_group.ancilla_id) + self.pivot,
                            width=diagonal_spacing,
                            height=diagonal_spacing,
                            rotation=self.identifier_to_rotation(parity_group),
                            alignment=TransformAlignment.MID_CENTER,
                            style_settings=StyleManager.read_config().plaquette_style_x,
                        )
                    )
                else:
                    result.append(
                        TrianglePlaquette(
                            pivot=self.identifier_to_pivot(parity_group.ancilla_id) + self.pivot,
                            width=diagonal_spacing,
                            height=diagonal_spacing,
                            rotation=self.identifier_to_rotation(parity_group),
                            alignment=TransformAlignment.MID_CENTER,
                            style_settings=StyleManager.read_config().plaquette_style_x,
                        )
                    )
        for parity_group in self.connectivity.parity_group_z:
            ancilla_coordinates: Vec2D = self.identifier_to_pivot(identifier=parity_group.ancilla_id)
            relative_coordinates: List[Vec2D] = [
                self.identifier_to_pivot(identifier=qubit_id) - ancilla_coordinates
                for qubit_id in parity_group.data_ids
            ]
            mean_relative_coordinates: Vec2D = Vec2D(
                x=np.mean([v.x for v in relative_coordinates]),
                y=np.mean([v.y for v in relative_coordinates]),
            )
            mean_center: bool = all(np.isclose(mean_relative_coordinates.to_vector(), Vec2D(0.0, 0.0).to_vector()))

            if len(parity_group.data_ids) == 4:
                result.append(
                    RectanglePlaquette(
                        pivot=self.identifier_to_pivot(parity_group.ancilla_id) + self.pivot,
                        width=diagonal_spacing,
                        height=diagonal_spacing,
                        rotation=self.identifier_to_rotation(parity_group),
                        alignment=TransformAlignment.MID_CENTER,
                        style_settings=StyleManager.read_config().plaquette_style_z,
                    )
                )
            if len(parity_group.data_ids) == 2:
                if mean_center:
                    print(self.identifier_to_rotation(parity_group))
                    result.append(
                        DiagonalPlaquette(
                            pivot=self.identifier_to_pivot(parity_group.ancilla_id) + self.pivot,
                            width=diagonal_spacing,
                            height=diagonal_spacing,
                            rotation=self.identifier_to_rotation(parity_group),
                            alignment=TransformAlignment.MID_CENTER,
                            style_settings=StyleManager.read_config().plaquette_style_z,
                        )
                    )
                else:
                    result.append(
                        TrianglePlaquette(
                            pivot=self.identifier_to_pivot(parity_group.ancilla_id) + self.pivot,
                            width=diagonal_spacing,
                            height=diagonal_spacing,
                            rotation=self.identifier_to_rotation(parity_group),
                            alignment=TransformAlignment.MID_CENTER,
                            style_settings=StyleManager.read_config().plaquette_style_z,
                        )
                    )
        return result

    def get_element_components(self) -> List[IDrawComponent]:
        result: List[IDrawComponent] = []
        for qubit_id in self.connectivity.qubit_ids:
            result.append(DotComponent(
                pivot=self.identifier_to_pivot(qubit_id) + self.pivot,
                alignment=TransformAlignment.MID_CENTER,
            ))
            result.append(TextComponent(
                pivot=self.identifier_to_pivot(qubit_id) + self.pivot,
                text=qubit_id.id,
                alignment=TransformAlignment.MID_CENTER,
            ))
        return result

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

    def identifier_to_rotation(self, identifier: Union[IQubitID, IParityGroup]) -> float:
        """:return: Rotation based on (parity group) ancilla identifier."""
        rotation_offset: float = -45
        hexagon_rotation: float = 30
        # Guard clause, if identifier is data qubit or not present in ancilla group
        is_single_qubit_id: bool = isinstance(identifier, IQubitID)
        if is_single_qubit_id:
            if identifier in self.connectivity.data_qubit_ids:
                return self.rotation + rotation_offset + hexagon_rotation
            return self.rotation + rotation_offset
        identifier: IParityGroup

        # Guard clause, if weight-4 plaquette, return default
        if len(identifier.data_ids) == 4:
            return self.rotation + rotation_offset

        ancilla_coordinates: Vec2D = self.identifier_to_pivot(identifier=identifier.ancilla_id)
        relative_coordinates: List[Vec2D] = [
            self.identifier_to_pivot(identifier=qubit_id) - ancilla_coordinates
            for qubit_id in identifier.data_ids
        ]
        mean_relative_coordinates: Vec2D = Vec2D(
            x=np.mean([v.x for v in relative_coordinates]),
            y=np.mean([v.y for v in relative_coordinates]),
        )
        mean_center: bool = all(np.isclose(mean_relative_coordinates.to_vector(), Vec2D(0.0, 0.0).to_vector()))

        if mean_center:  # Weight-2 diagonal
            line = Line2D(start=relative_coordinates[0], end=relative_coordinates[1])
            slope = (line.end.y - line.start.y) / (line.end.x - line.start.x)
            if slope == +1.0:
                pass
            elif slope == -1.0:
                rotation_offset += 90
        else:  # Weight-2 triangle
            if mean_relative_coordinates.x == 0.0 and mean_relative_coordinates.y > 0.0:
                rotation_offset += 90
            elif mean_relative_coordinates.x == 0.0 and mean_relative_coordinates.y < 0.0:
                rotation_offset += 270
            elif mean_relative_coordinates.x > 0.0 and mean_relative_coordinates.y == 0.0:
                rotation_offset += 0
            elif mean_relative_coordinates.x < 0.0 and mean_relative_coordinates.y == 0.0:
                rotation_offset += 180

        if identifier.ancilla_id in self.connectivity.ancilla_qubit_ids:
            return self.rotation + rotation_offset
        return self.rotation  # default
    # endregion


@dataclass(frozen=True)
class AllGreyVisualConnectivityDescription(VisualConnectivityDescription):
    """
    Data class, overwriting VisualConnectivityDescription by forcing single plaquette color.
    """
    plaquette_color_overwrite: str = field(default="#b0b0b0")

    # region Class Methods
    def get_plaquette_components(self) -> List[IDrawComponent]:
        result: List[IDrawComponent] = []
        diagonal_spacing: float = self.layout_spacing * np.sqrt(2)

        style_settings = StyleManager.read_config().plaquette_style_x
        style_settings = PlaquetteStyleSettings(
            background_color=self.plaquette_color_overwrite,
            line_color=style_settings.line_color,
            line_width=style_settings.line_width,
            zorder=style_settings.zorder,
        )

        for parity_group in self.connectivity.parity_group_x:
            if len(parity_group.data_ids) == 4:
                result.append(
                    RectanglePlaquette(
                        pivot=self.identifier_to_pivot(parity_group.ancilla_id) + self.pivot,
                        width=diagonal_spacing,
                        height=diagonal_spacing,
                        rotation=self.identifier_to_rotation(parity_group),
                        alignment=TransformAlignment.MID_CENTER,
                        style_settings=style_settings,
                    )
                )
            if len(parity_group.data_ids) == 2:
                result.append(
                    TrianglePlaquette(
                        pivot=self.identifier_to_pivot(parity_group.ancilla_id) + self.pivot,
                        width=diagonal_spacing,
                        height=diagonal_spacing,
                        rotation=self.identifier_to_rotation(parity_group),
                        alignment=TransformAlignment.MID_CENTER,
                        style_settings=style_settings,
                    )
                )
        for parity_group in self.connectivity.parity_group_z:
            if len(parity_group.data_ids) == 4:
                result.append(
                    RectanglePlaquette(
                        pivot=self.identifier_to_pivot(parity_group.ancilla_id) + self.pivot,
                        width=diagonal_spacing,
                        height=diagonal_spacing,
                        rotation=self.identifier_to_rotation(parity_group),
                        alignment=TransformAlignment.MID_CENTER,
                        style_settings=style_settings,
                    )
                )
            if len(parity_group.data_ids) == 2:
                result.append(
                    TrianglePlaquette(
                        pivot=self.identifier_to_pivot(parity_group.ancilla_id) + self.pivot,
                        width=diagonal_spacing,
                        height=diagonal_spacing,
                        rotation=self.identifier_to_rotation(parity_group),
                        alignment=TransformAlignment.MID_CENTER,
                        style_settings=style_settings,
                    )
                )
        return result
    # endregion


@dataclass(frozen=True)
class StabilizerGroupVisualConnectivityDescription(VisualConnectivityDescription):
    """
    Data class, overwriting VisualConnectivityDescription by implementing stabilizer group element visualization.
    """
    element_color_overwrite: str = field(default="#c4c4c4")

    # region Class Methods
    def get_element_components(self) -> List[IDrawComponent]:
        result: List[IDrawComponent] = []
        style_setting: StyleSettings = StyleManager.read_config()

        for qubit_id in self.connectivity.qubit_ids:
            background_color = self.element_color_overwrite
            if qubit_id in [parity_group.ancilla_id for parity_group in self.connectivity.parity_group_z]:
                background_color = style_setting.color_background_z
            if qubit_id in [parity_group.ancilla_id for parity_group in self.connectivity.parity_group_x]:
                background_color = style_setting.color_background_x

            result.append(DotComponent(
                pivot=self.identifier_to_pivot(qubit_id) + self.pivot,
                alignment=TransformAlignment.MID_CENTER,
                style_settings=ElementStyleSettings(
                    background_color=background_color,
                    line_color=style_setting.color_element,
                    element_radius=style_setting.radius_dot,
                    zorder=style_setting.zorder_element,
                ),
            ))
            result.append(TextComponent(
                pivot=self.identifier_to_pivot(qubit_id) + self.pivot,
                text=qubit_id.id,
                alignment=TransformAlignment.MID_CENTER,
            ))
        return result
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
    if not isinstance(axes, Iterable):
        axes = [axes]

    for i, ax in enumerate(axes):
        descriptor: VisualConnectivityDescription = VisualConnectivityDescription(
            connectivity=Surface17Layer(),
            gate_sequence=description.get_gate_sequence_at_index(i),
            layout_spacing=1.0
        )
        kwargs[SubplotKeywordEnum.HOST_AXES.value] = (fig, ax)
        plot_layout_description(descriptor, **kwargs)
    return fig, axes[0]


def plot_stabilizer_specific_gate_sequences(description: IGenericSurfaceCodeLayer, **kwargs) -> IFigureAxesPair:
    """
    Constructs a similar gate sequence plot as 'plot_gate_sequences'.
    However, the gate-sequence info is taken from description parameter
     and background-layout is taken from the parity-group part of the description parameter.
    Allowing for extra flexibility.
    :param description: Generic surface code layer definition including parity-groups and gate sequence.
    :param kwargs: Keyword arguments passed to figure constructor.
    :return: Figure and Axes pair.
    """
    sequence_count: int = description.gate_sequence_count
    kwargs[SubplotKeywordEnum.FIGURE_SIZE.value] = (5 * sequence_count, 5)
    fig, axes = construct_subplot(ncols=sequence_count, **kwargs)
    if not isinstance(axes, Iterable):
        axes = [axes]

    for i, ax in enumerate(axes):
        descriptor: AllGreyVisualConnectivityDescription = AllGreyVisualConnectivityDescription(
            connectivity=Surface17Layer(),
            gate_sequence=description.get_gate_sequence_at_index(i),
            layout_spacing=1.0
        )
        kwargs[SubplotKeywordEnum.HOST_AXES.value] = (fig, ax)
        fig, ax = plot_layout_description(descriptor, **kwargs)

        descriptor: StabilizerGroupVisualConnectivityDescription = StabilizerGroupVisualConnectivityDescription(
            connectivity=description,
            gate_sequence=description.get_gate_sequence_at_index(i),
            layout_spacing=1.0
        )
        kwargs[SubplotKeywordEnum.HOST_AXES.value] = (fig, ax)
        plot_layout_description(descriptor, **kwargs)
    return fig, axes[0]