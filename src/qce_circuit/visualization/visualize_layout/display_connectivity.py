# -------------------------------------------
# Module containing visualization for ISurfaceCodeLayer.
# -------------------------------------------
from dataclasses import dataclass, field
from collections.abc import Iterable
from typing import Dict, List, Union, Optional
import numpy as np
import math
from qce_circuit.connectivity.intrf_channel_identifier import IQubitID, QubitIDObj
from qce_circuit.connectivity.intrf_connectivity_surface_code import ISurfaceCodeLayer, IParityGroup
from qce_circuit.connectivity.connectivity_surface_code import Surface17Layer, StabilizerType
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
    LineComponent,
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
    include_element_labels: bool = field(default=True)

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
                # Process unique data-qubit stabilizer type plaquettes
                for parity_data_qubit_id in parity_group.data_ids:
                    stabilizer_type: StabilizerType = parity_group.get_stabilizer_type(parity_data_qubit_id)
                    if stabilizer_type == StabilizerType.STABILIZER_X:
                        continue
                    draw_element = RectanglePlaquette(
                        pivot=(self.identifier_to_pivot(parity_data_qubit_id) + self.identifier_to_pivot(parity_group.ancilla_id)) * 0.5 + self.pivot,
                        width=0.5 * diagonal_spacing,
                        height=0.5 * diagonal_spacing,
                        rotation=self.identifier_to_rotation(parity_group),
                        alignment=TransformAlignment.MID_CENTER,
                        style_settings=StyleManager.read_config().plaquette_style_z,
                    )
                    result.append(draw_element)

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
                    # Process unique data-qubit stabilizer type plaquettes
                    for parity_data_qubit_id in parity_group.data_ids:
                        stabilizer_type: StabilizerType = parity_group.get_stabilizer_type(parity_data_qubit_id)
                        if stabilizer_type == StabilizerType.STABILIZER_Z:
                            continue
                        raise NotImplementedError(f"Unique data-qubit stabilizer visualization not yet supported for diagonal stabilizers.")
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
                    # Process unique data-qubit stabilizer type plaquettes
                    for parity_data_qubit_id in parity_group.data_ids:
                        stabilizer_type: StabilizerType = parity_group.get_stabilizer_type(parity_data_qubit_id)
                        if stabilizer_type == StabilizerType.STABILIZER_X:
                            continue
                        triangle_scalar: float = 1 / math.sqrt(2)
                        draw_element = TrianglePlaquette(
                            pivot=mean_relative_coordinates + self.identifier_to_pivot(parity_group.ancilla_id) + self.pivot,
                            width=triangle_scalar * diagonal_spacing,
                            height=triangle_scalar * diagonal_spacing,
                            rotation=self.get_rotation_offset_from_relative_direction(
                                start=self.identifier_to_pivot(parity_group.ancilla_id),
                                end=self.identifier_to_pivot(parity_data_qubit_id),
                                mean_relative_coordinates=mean_relative_coordinates,
                            ) + 45,
                            alignment=TransformAlignment.MID_CENTER,
                            style_settings=StyleManager.read_config().plaquette_style_z,
                        )
                        result.append(draw_element)

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
                # Process unique data-qubit stabilizer type plaquettes
                for parity_data_qubit_id in parity_group.data_ids:
                    stabilizer_type: StabilizerType = parity_group.get_stabilizer_type(parity_data_qubit_id)
                    if stabilizer_type == StabilizerType.STABILIZER_Z:
                        continue
                    draw_element = RectanglePlaquette(
                        pivot=(self.identifier_to_pivot(parity_data_qubit_id) + self.identifier_to_pivot(parity_group.ancilla_id)) * 0.5 + self.pivot,
                        width=0.5 * diagonal_spacing,
                        height=0.5 * diagonal_spacing,
                        rotation=self.identifier_to_rotation(parity_group),
                        alignment=TransformAlignment.MID_CENTER,
                        style_settings=StyleManager.read_config().plaquette_style_x,
                    )
                    result.append(draw_element)

            if len(parity_group.data_ids) == 2:
                if mean_center:
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
                    # Process unique data-qubit stabilizer type plaquettes
                    for parity_data_qubit_id in parity_group.data_ids:
                        stabilizer_type: StabilizerType = parity_group.get_stabilizer_type(parity_data_qubit_id)
                        if stabilizer_type == StabilizerType.STABILIZER_Z:
                            continue
                        raise NotImplementedError(f"Unique data-qubit stabilizer visualization not yet supported for diagonal stabilizers.")
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
                    # Process unique data-qubit stabilizer type plaquettes
                    for parity_data_qubit_id in parity_group.data_ids:
                        stabilizer_type: StabilizerType = parity_group.get_stabilizer_type(parity_data_qubit_id)
                        if stabilizer_type == StabilizerType.STABILIZER_Z:
                            continue
                        triangle_scalar: float = 1 / math.sqrt(2)
                        draw_element = TrianglePlaquette(
                            pivot=mean_relative_coordinates + self.identifier_to_pivot(parity_group.ancilla_id) + self.pivot,
                            width=triangle_scalar * diagonal_spacing,
                            height=triangle_scalar * diagonal_spacing,
                            rotation=self.get_rotation_offset_from_relative_direction(
                                start=self.identifier_to_pivot(parity_group.ancilla_id),
                                end=self.identifier_to_pivot(parity_data_qubit_id),
                                mean_relative_coordinates=mean_relative_coordinates,
                            ) + 45,
                            alignment=TransformAlignment.MID_CENTER,
                            style_settings=StyleManager.read_config().plaquette_style_x,
                        )
                        result.append(draw_element)
        return result

    def get_element_components(self) -> List[IDrawComponent]:
        result: List[IDrawComponent] = []
        for qubit_id in self.connectivity.qubit_ids:
            result.append(DotComponent(
                pivot=self.identifier_to_pivot(qubit_id) + self.pivot,
                alignment=TransformAlignment.MID_CENTER,
            ))
            if self.include_element_labels:
                result.append(TextComponent(
                    pivot=self.identifier_to_pivot(qubit_id) + self.pivot,
                    text=qubit_id.id,
                    alignment=TransformAlignment.MID_CENTER,
                ))
        return result

    def get_element_edges_components(self) -> List[IDrawComponent]:
        result: List[IDrawComponent] = []
        for edge_id in self.connectivity.edge_ids:
            result.append(LineComponent(
                pivot0=self.identifier_to_pivot(edge_id.qubit_ids[0]) + self.pivot,
                pivot1=self.identifier_to_pivot(edge_id.qubit_ids[1]) + self.pivot,
                alignment=TransformAlignment.MID_CENTER,
            ))
        return result

    def get_operation_components(self) -> List[IDrawComponent]:
        park_components: List[IDrawComponent] = [
            ParkingComponent(
                pivot=self.identifier_to_pivot(identifier=operation.identifier) + self.pivot,
                alignment=TransformAlignment.MID_CENTER,
            )
            for operation in self.gate_sequence.park_operations
        ]
        gate_components: List[IDrawComponent] = [
            GateOperationComponent(
                pivot0=self.identifier_to_pivot(identifier=operation.identifier.qubit_ids[0]) + self.pivot,
                pivot1=self.identifier_to_pivot(identifier=operation.identifier.qubit_ids[1]) + self.pivot,
                alignment=TransformAlignment.MID_CENTER,
            )
            for operation in self.gate_sequence.gate_operations
        ]
        return park_components + gate_components

    def identifier_to_pivot(self, identifier: IQubitID) -> Vec2D:
        """:return: Pivot based on qubit identifier."""
        if hasattr(self.connectivity, 'get_qubit_coordinates'):
            try:
                coord = self.connectivity.get_qubit_coordinates(identifier)
                return (coord * self.layout_spacing).rotate(np.deg2rad(self.rotation)) + self.pivot
            except Exception:
                return self.pivot
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
        rotation_offset += self.get_rotation_offset_from_relative_direction(
            start=relative_coordinates[0],
            end=relative_coordinates[1],
            mean_relative_coordinates=mean_relative_coordinates,
        )

        if identifier.ancilla_id in self.connectivity.ancilla_qubit_ids:
            return self.rotation + rotation_offset
        return self.rotation  # default
    # endregion

    @staticmethod
    def get_rotation_offset_from_relative_direction(start: Vec2D, end: Vec2D, mean_relative_coordinates: Vec2D) -> float:
        """
        :param start: Starting pivot of line from which we want to determine the rotation offset.
        :param end: Ending pivot of line from which we want to determine the rotation offset.
        :param mean_relative_coordinates: Relative mean coordinate of all data qubits compared to ancilla qubit.
            Needed to distinguish between (triangle) weight-2 and (diagonal) wheight-2 stabilizers.
        :return: Rotation offset [degree].
        """
        rotation_offset: float = 0
        absolute_tolerance: float = 1e-9
        mean_center: bool = all(np.isclose(mean_relative_coordinates.to_vector(), Vec2D(0.0, 0.0).to_vector()))

        if mean_center:  # Weight-2 diagonal
            line = Line2D(start=start, end=end)
            slope = (line.end.y - line.start.y) / (line.end.x - line.start.x)
            if math.isclose(slope, +1.0, abs_tol=absolute_tolerance):
                pass
            elif math.isclose(slope, -1.0, abs_tol=absolute_tolerance):
                rotation_offset += 90
        else:  # Weight-2 triangle
            if math.isclose(mean_relative_coordinates.x, 0.0, abs_tol=absolute_tolerance) and mean_relative_coordinates.y > 0.0:
                rotation_offset += 90
            elif math.isclose(mean_relative_coordinates.x, 0.0, abs_tol=absolute_tolerance) and mean_relative_coordinates.y < 0.0:
                rotation_offset += 270
            elif mean_relative_coordinates.x > 0.0 and math.isclose(mean_relative_coordinates.y, 0.0, abs_tol=absolute_tolerance):
                rotation_offset += 0
            elif mean_relative_coordinates.x < 0.0 and math.isclose(mean_relative_coordinates.y, 0.0, abs_tol=absolute_tolerance):
                rotation_offset += 180
        return rotation_offset


@dataclass(frozen=True)
class AllGreyVisualConnectivityDescription(VisualConnectivityDescription):
    """
    Data class, overwriting VisualConnectivityDescription by forcing single plaquette color.
    """
    plaquette_color_overwrite: str = field(default_factory=lambda: StyleManager.read_config().color_background_base)

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
    element_color_overwrite: str = field(default_factory=lambda: StyleManager.read_config().color_element)
    element_highlight_color_overwrite: str = field(default_factory=lambda: StyleManager.read_config().color_element_outline)
    include_gate_sequence_labels: bool = field(default=False)

    # region Class Methods
    def get_element_components(self) -> List[IDrawComponent]:
        result: List[IDrawComponent] = []
        style_setting: StyleSettings = StyleManager.read_config()
        gate_sequence_data_qubit_ids: List[IQubitID] = [qubit_id for qubit_id in self.gate_sequence.qubit_ids if qubit_id in self.connectivity.data_qubit_ids]

        for qubit_id in self.connectivity.qubit_ids:
            background_color = self.element_color_overwrite
            if qubit_id in [parity_group.ancilla_id for parity_group in self.connectivity.parity_group_z]:
                background_color = style_setting.color_background_z
            if qubit_id in [parity_group.ancilla_id for parity_group in self.connectivity.parity_group_x]:
                background_color = style_setting.color_background_x
            if qubit_id in gate_sequence_data_qubit_ids:
                background_color = self.element_highlight_color_overwrite

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
            if self.include_element_labels or (self.include_gate_sequence_labels and qubit_id in self.gate_sequence.qubit_ids):
                result.append(TextComponent(
                    pivot=self.identifier_to_pivot(qubit_id) + self.pivot,
                    text=qubit_id.id,
                    alignment=TransformAlignment.MID_CENTER,
                ))
        return result
    # endregion


def plot_layout_description(description: VisualConnectivityDescription, **kwargs) -> IFigureAxesPair:
    # Calculate span to adapt figure size automatically
    x_coords = [description.identifier_to_pivot(qubit_id).x for qubit_id in description.connectivity.qubit_ids]
    y_coords = [description.identifier_to_pivot(qubit_id).y for qubit_id in description.connectivity.qubit_ids]
    x_span = (max(x_coords) - min(x_coords)) if x_coords else 5
    y_span = (max(y_coords) - min(y_coords)) if y_coords else 5
    
    # Use a base scaling factor to maintain text-to-circle proportion
    # Default Surface-17 size is roughly span=4 -> figure_size=5. So factor = 1.25.
    default_fig_size = (x_span * 1.25 + 1.0, y_span * 1.25 + 1.0)

    # Data allocation
    kwargs[SubplotKeywordEnum.FIGURE_SIZE.value] = kwargs.get(SubplotKeywordEnum.FIGURE_SIZE.value, default_fig_size)
    kwargs[SubplotKeywordEnum.AXES_FORMAT.value] = kwargs.get(SubplotKeywordEnum.AXES_FORMAT.value, CircuitAxesFormat())
    kwargs[SubplotKeywordEnum.LABEL_FORMAT.value] = LabelFormat(x_label='', y_label='')
    fig, ax = construct_subplot(**kwargs)

    for draw_component in description.get_plaquette_components():
        draw_component.draw(axes=ax)

    for draw_component in description.get_element_components():
        draw_component.draw(axes=ax)

    for draw_component in description.get_element_edges_components():
        draw_component.draw(axes=ax)

    for draw_component in description.get_operation_components():
        draw_component.draw(axes=ax)

    ax.set_aspect('equal')
    ax.autoscale(enable=True, axis='both', tight=True)
    ax.margins(0.01)
    ax.relim()
    ax.autoscale_view()
    fig.tight_layout()
    return fig, ax


def plot_gate_sequences(description: IGenericSurfaceCodeLayer, **kwargs) -> IFigureAxesPair:
    sequence_count: int = description.gate_sequence_count
    kwargs[SubplotKeywordEnum.FIGURE_SIZE.value] = (5 * sequence_count, 5)
    fig, axes = construct_subplot(ncols=sequence_count, **kwargs)
    if not isinstance(axes, Iterable):
        axes = [axes]

    for i, ax in enumerate(axes):
        descriptor: VisualConnectivityDescription = VisualConnectivityDescription(
            connectivity=description.background_surface_layer,
            gate_sequence=description.get_gate_sequence_at_index(i),
            layout_spacing=1.0
        )
        kwargs[SubplotKeywordEnum.HOST_AXES.value] = (fig, ax)
        plot_layout_description(descriptor, **kwargs)
    return fig, axes[0]


def plot_stabilizer_specific_gate_sequences(description: IGenericSurfaceCodeLayer, include_element_labels: bool = True, include_gate_sequence_element_labels: bool = True, connectivity: Optional[ISurfaceCodeLayer] = None, **kwargs) -> IFigureAxesPair:
    """
    Constructs a similar gate sequence plot as 'plot_gate_sequences'.
    However, the gate-sequence info is taken from description parameter
     and background-layout is taken from the parity-group part of the description parameter.
    Allowing for extra flexibility.
    :param description: Generic surface code layer definition including parity-groups and gate sequence.
    :param kwargs: Keyword arguments passed to figure constructor.
    :param include_element_labels: Boolean to enable or disable element label text.
    :param include_gate_sequence_element_labels: Boolean to enable or disable (gate sequence only) element label text.
    :param connectivity: Optional connectivity layer to use as background. If None, uses description.background_surface_layer.
    :return: Figure and Axes pair.
    """
    if connectivity is None:
        connectivity = description.background_surface_layer

    sequence_count: int = description.gate_sequence_count
    kwargs[SubplotKeywordEnum.FIGURE_SIZE.value] = (5 * sequence_count, 5)
    fig, axes = construct_subplot(ncols=sequence_count, **kwargs)
    if not isinstance(axes, Iterable):
        axes = [axes]

    for i, ax in enumerate(axes):
        descriptor: AllGreyVisualConnectivityDescription = AllGreyVisualConnectivityDescription(
            connectivity=connectivity,
            gate_sequence=description.get_gate_sequence_at_index(i),
            layout_spacing=1.0,
            include_element_labels=include_element_labels,
        )
        kwargs[SubplotKeywordEnum.HOST_AXES.value] = (fig, ax)
        fig, ax = plot_layout_description(descriptor, **kwargs)

        descriptor: StabilizerGroupVisualConnectivityDescription = StabilizerGroupVisualConnectivityDescription(
            connectivity=description,
            gate_sequence=description.get_gate_sequence_at_index(i),
            layout_spacing=1.0,
            include_element_labels=include_element_labels,
            include_gate_sequence_labels=include_gate_sequence_element_labels,
        )
        kwargs[SubplotKeywordEnum.HOST_AXES.value] = (fig, ax)
        plot_layout_description(descriptor, **kwargs)
    return fig, axes[0]
