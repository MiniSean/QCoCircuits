# -------------------------------------------
# Module containing visualization for ICircuitCompositeOperation.
# -------------------------------------------
from dataclasses import dataclass, field
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Optional, TypeVar, Dict, Any, Tuple
from qce_circuit.structure.intrf_circuit_operation import RelationLink
from qce_circuit.structure.circuit_operations import (
    Reset,
    Wait,
    Rx180,
    Rx90,
    Rxm90,
    Ry180,
    Ry90,
    Rym90,
    Rx180ef,
    VirtualPhase,
    Rphi90,
    CPhase,
    TwoQubitOperation,
    DispersiveMeasure,
    Identity,
    Hadamard,
    Barrier,
    VirtualPark,
    VirtualVacant,
    VirtualTwoQubitVacant,
    VirtualEmpty,
)
from qce_circuit.visualization.visualize_circuit.draw_components.annotation_components import (
    HorizontalVariableIndicator,
)
from qce_circuit.visualization.visualize_circuit.draw_components.channel_components import (
    ChannelHeader,
    ChannelBar,
)
from qce_circuit.visualization.visualize_circuit.draw_components.transform_constructor import TransformConstructor
from qce_circuit.visualization.visualize_circuit.intrf_draw_component import IDrawComponent
from qce_circuit.utilities.geometric_definitions import (
    IRectTransformComponent,
    IRectTransform,
    TransformAlignment,
    DynamicLength,
    FixedLength,
    FixedPivot,
    Vec2D,
)
from qce_circuit.visualization.visualize_circuit.draw_components.operation_components import (
    RotationAxis,
    RotationAngle,
    GateType,
    BlockMeasure,
    BlockRotation,
    BlockGate,
)
from qce_circuit.visualization.visualize_circuit.draw_components.multi_pivot_components import (
    BlockTwoQubitGate,
)
from qce_circuit.language.declarative_circuit import (
    IDeclarativeCircuit,
    InitialStateEnum,
)
from qce_circuit.structure.intrf_circuit_operation import (
    IDurationComponent,
    ICircuitOperation,
    ChannelIdentifier,
)
from qce_circuit.structure.intrf_circuit_operation_composite import (
    ICircuitCompositeOperation,
)
from qce_circuit.structure.registry_duration import (
    temporary_override_get_registry_at,
    GlobalRegistryKey,
)
from qce_circuit.utilities.custom_context_managers import clear_lru_cache
from qce_circuit.visualization.visualize_circuit.intrf_factory_draw_components import (
    ITransformConstructor,
    DrawComponentFactoryManager,
    BulkDrawComponentFactoryManager,
)
from qce_circuit.visualization.visualize_circuit.draw_components.factory_draw_components import (
    DefaultFactory,
    MeasureFactory,
    TwoQubitBlockFactory,
    Rx180Factory,
    Rx90Factory,
    Rxm90Factory,
    Ry180Factory,
    Ry90Factory,
    Rym90Factory,
    Rx180efFactory,
    ZPhaseFactory,
    Rphi90Factory,
    ResetFactory,
    WaitFactory,
    IdentityFactory,
    FootprintFactory,
    HadamardFactory,
    BarrierFactory,
    VirtualParkFactory,
    VirtualVacantFactory,
    VirtualTwoQubitVacantFactory,
    VirtualEmptyFactory,
)
from qce_circuit.visualization.visualize_circuit.draw_components.factory_multi_draw_components import \
    MultiTwoQubitBlockFactory
from qce_circuit.utilities.array_manipulation import unique_in_order
from qce_circuit.visualization.visualize_circuit.plotting_functionality import (
    construct_subplot,
    SubplotKeywordEnum,
    IAxesFormat,
    AxesFormat,
    LabelFormat,
    IFigureAxesPair,
)


VISUALIZATION_DURATION_REGISTRY = {
    GlobalRegistryKey.READOUT: 2.0,
    GlobalRegistryKey.MICROWAVE: 1.0,
    GlobalRegistryKey.FLUX: 1.0,
    GlobalRegistryKey.RESET: 2.0,
}


@dataclass(frozen=True)
class VisualCircuitDescription:
    """
    Data class, containing all information required to draw circuit.
    Implements basic visualization.
    """
    channel_height: float
    channel_width: float
    channel_indices: List[int]
    """Array of unique, ordered channel indices."""
    channel_states: List[InitialStateEnum]
    operations: List[ICircuitOperation]
    """Array of operations are duration component."""
    composite_operations: List[ICircuitCompositeOperation]
    """Array of composite operations."""
    channel_label_map: Dict[int, str] = field(default_factory=dict)

    # region Class Properties
    @property
    def channel_spacing(self) -> float:
        return self.channel_height * 1.2

    @property
    def figure_size(self) -> Tuple[float, float]:
        """:return: Figure size (x, y) depending on visualized circuit components."""
        return (self.channel_width, self.channel_spacing * len(self.channel_indices))
    # endregion

    # region Class Methods
    def get_channel_bar(self, index: int) -> ChannelBar:
        """:return: Channel bar drawing components."""
        return ChannelBar(
            pivot=Vec2D(x=0, y=-1 * index * self.channel_spacing),
            width=self.channel_width,
            height=self.channel_height,
        )

    def get_channel_header(self, index: int) -> ChannelHeader:
        """:return: Channel header drawing components."""
        channel_index = self.channel_indices[index]
        channel_name: str = f'# {channel_index}'
        # Temporary way to specify channel index labels
        if index in self.channel_label_map:
            channel_name = f'{self.channel_label_map[index]}'

        channel_state = self.channel_states[index].value
        return ChannelHeader(
            pivot=Vec2D(x=0, y=-1 * index * self.channel_spacing),
            height=FixedLength(self.channel_height),
            channel_name=channel_name,
            state_description=rf'$|{channel_state}\rangle$',
        )

    def get_transform_constructor(self) -> TransformConstructor:
        return TransformConstructor(
            channel_height=self.channel_height,
            channel_spacing=self.channel_spacing,
            channel_indices=self.channel_indices,
        )

    def get_operation_draw_components(self) -> List[IDrawComponent]:
        factory_manager: BulkDrawComponentFactoryManager = BulkDrawComponentFactoryManager(
            individual_component_factory=DrawComponentFactoryManager(
                default_factory=DefaultFactory(),
                factory_lookup={
                    CPhase: TwoQubitBlockFactory(),
                    DispersiveMeasure: MeasureFactory(),
                    Reset: ResetFactory(),
                    Wait: WaitFactory(),
                    Rx180: Rx180Factory(),
                    Rx90: Rx90Factory(),
                    Rxm90: Rxm90Factory(),
                    Ry180: Ry180Factory(),
                    Ry90: Ry90Factory(),
                    Rym90: Rym90Factory(),
                    Rx180ef: Rx180efFactory(),
                    Rphi90: Rphi90Factory(),
                    VirtualPhase: ZPhaseFactory(),
                    Identity: IdentityFactory(),
                    Hadamard: HadamardFactory(),
                    Barrier: BarrierFactory(),
                    VirtualPark: VirtualParkFactory(),
                    VirtualVacant: VirtualVacantFactory(),
                    VirtualTwoQubitVacant: VirtualTwoQubitVacantFactory(),
                    VirtualEmpty: VirtualEmptyFactory(),
                }
            ),
            factory_lookup={
                TwoQubitOperation: MultiTwoQubitBlockFactory(factory_lookup={
                    CPhase: TwoQubitBlockFactory(),
                    VirtualTwoQubitVacant: VirtualTwoQubitVacantFactory()
                }),
            }
        )
        transform_constructor: TransformConstructor = self.get_transform_constructor()
        return factory_manager.construct(
            operations=self.operations,
            transform_constructor=transform_constructor,
        )

    def get_highlight_draw_components(self) -> List[IDrawComponent]:
        # Data allocation
        result: List[IDrawComponent] = []
        factory: FootprintFactory = FootprintFactory()
        transform_constructor: TransformConstructor = self.get_transform_constructor()

        for composite_operation in self.composite_operations:
            # Ignore highlight if repetition number is 1
            if composite_operation.nr_of_repetitions == 1:
                continue

            result.append(factory.construct(
                operation=composite_operation,
                transform_constructor=transform_constructor,
            ))
        return result
    # endregion


T = TypeVar("T")


def reorder_indices(original_order: List[T], specific_order: List[T]) -> List[T]:
    """
    Reorders an array of indices based on a specified order.
    :raises: (ValueError) If any index in specific_order is not in original_order.
    :param original_order: (list of T) The original order of indices.
    :param specific_order: (list of T) The specific order to prioritize in the result.
    :return: (list of T) The reordered array of indices.
    """

    # Check if all elements in specific_order are in original_order
    if not all(item in original_order for item in specific_order):
        raise ValueError(f"All indices in specific_order must be in original_order. Instead got {specific_order}, {original_order}")

    # Create the reordered list
    reordered_list = specific_order + [item for item in original_order if item not in specific_order]

    return reordered_list


def reorder_map(original_order: Dict[T, Any], specific_order: List[T]) -> Dict[T, Any]:
    """
    Reorders map of indices (to any) based on a specified order.
    :raises: (ValueError) If any index in specific_order is not in original_order.
    :param original_order: (Dict of T as keys) The original order of indices.
    :param specific_order: (list of T) The specific order to prioritize in the result.
    :return: (Dict of T as keys) The reordered array of indices.
    """
    original_keys: List[T] = list(original_order.keys())

    # Create the reordered list
    ordered_keys: List[T] = specific_order + [item for item in original_keys if item not in specific_order]

    result: Dict[T, Any] = {}
    for original_key, ordered_key in zip(original_keys, ordered_keys):
        result[ordered_key] = original_order[original_key]
    return result


def construct_visual_description(circuit: IDeclarativeCircuit, custom_channel_order: Optional[List[int]] = None, custom_channel_map: Optional[Dict[int, str]] = None) -> VisualCircuitDescription:
    """:return: Draw description based on declarative circuit interface instance."""
    channel_indices: List[int] = unique_in_order([identifier.id for identifier in circuit.occupied_qubit_channels])
    # Apply custom channel order
    if custom_channel_order is None:
        custom_channel_order = []
    # Construct custom channel map
    if custom_channel_map is None:
        custom_channel_map = {
            channel_index: channel_index
            for channel_index in channel_indices
        }
    channel_indices = reorder_indices(original_order=channel_indices, specific_order=custom_channel_order)
    # Apply custom channel map
    custom_channel_map = {
        i: custom_channel_map[channel_index]
        for i, channel_index in enumerate(channel_indices)
    }
    # custom_channel_map = reorder_map(original_order=custom_channel_map, specific_order=custom_channel_order)
    channel_states: List[InitialStateEnum] = [circuit.get_qubit_initial_state(channel_index=channel_index) for channel_index in channel_indices]

    operations: List[ICircuitOperation] = circuit.operations
    # Determine end-time
    end_time: float = 1.0
    for operation in operations:
        if operation.end_time > end_time:
            end_time = operation.end_time

    return VisualCircuitDescription(
        channel_width=end_time + 1.0,
        channel_height=1.0,
        channel_indices=channel_indices,
        channel_label_map=custom_channel_map,
        channel_states=channel_states,
        operations=operations,
        composite_operations=circuit.composite_operations,
    )


def draw_transform_object(rect_transform: IRectTransform, axes: plt.Axes) -> plt.Axes:
    """Debug drawing of rectilinear transform component."""
    rectangle = patches.Rectangle(
        xy=rect_transform.origin_pivot.to_tuple(),
        width=rect_transform.width,
        height=rect_transform.height,
        linewidth=1.0,
        linestyle='--',
        edgecolor='red',
        facecolor='none',
        zorder=10,
    )
    parent_pivot = patches.Circle(
        xy=rect_transform.pivot.to_tuple(),
        radius=0.1,
        edgecolor='red',
        facecolor='none',
        zorder=11,
    )
    axes.add_patch(rectangle)
    axes.add_patch(parent_pivot)
    return axes


def draw_transform_component(component: IRectTransformComponent, axes: plt.Axes) -> plt.Axes:
    """Debug drawing of rectilinear transform component."""
    return draw_transform_object(rect_transform=component.rectilinear_transform, axes=axes)


class CircuitAxesFormat(IAxesFormat):
    """
    Specifies axis formatting for circuit visualization.
    """

    # region Interface Methods
    def apply_to_axes(self, axes: plt.Axes) -> plt.Axes:
        """
        Applies axes formatting settings to axis.
        :param axes: Axes to be formatted.
        :return: Updated Axes.
        """
        axes.set_axisbelow(True)  # Puts grid on background
        axes.set_aspect('equal', adjustable='box')  # Ensures the aspect ratio stays equal and adapts to internal data
        # Assuming ax is an Axes instance
        fig = axes.get_figure()
        fig.subplots_adjust(left=0.0, bottom=0.0, right=1.0, top=1.0, wspace=0.0, hspace=0.0)

        # Remove ticks
        axes.set_xticks([])
        axes.set_yticks([])
        # Remove background
        axes.set_frame_on(False)
        return axes
    # endregion

    # region Static Class Methods
    @staticmethod
    def default() -> 'AxesFormat':
        """:return: Default AxesFormat instance."""
        return AxesFormat()
    # endregion


def plot_debug(**kwargs) -> IFigureAxesPair:
    # Data allocation
    kwargs[SubplotKeywordEnum.AXES_FORMAT.value] = CircuitAxesFormat()
    fig, ax = construct_subplot(**kwargs)

    BlockMeasure(
        pivot=Vec2D(2.0, 1.25),
        width=2.0,
        height=0.5,
        alignment=TransformAlignment.MID_LEFT,
    ).draw(axes=ax)

    BlockRotation(
        pivot=Vec2D(0.0, 1.25),
        height=0.5,
        alignment=TransformAlignment.MID_LEFT,
    ).draw(axes=ax)
    BlockRotation(
        pivot=Vec2D(0.0, 2.0),
        height=0.5,
        alignment=TransformAlignment.MID_LEFT,
        rotation_axes=RotationAxis.X,
        rotation_angle=RotationAngle.RAD90,
    ).draw(axes=ax)
    BlockRotation(
        pivot=Vec2D(0.0, 2.75),
        height=0.5,
        alignment=TransformAlignment.MID_LEFT,
        rotation_axes=RotationAxis.Z,
        rotation_angle=RotationAngle.RAD180,
    ).draw(axes=ax)
    BlockRotation(
        pivot=Vec2D(1.0, 2.75),
        height=1.0,
        alignment=TransformAlignment.MID_LEFT,
        rotation_axes=RotationAxis.Z,
        rotation_angle=RotationAngle.RAD180,
    ).draw(axes=ax)

    BlockGate(
        pivot=Vec2D(-0.75, 1.25),
        height=0.5,
        alignment=TransformAlignment.MID_LEFT,
    ).draw(axes=ax)
    BlockGate(
        pivot=Vec2D(-0.75, 2.0),
        height=0.5,
        alignment=TransformAlignment.MID_LEFT,
        gate_type=GateType.X,
        rotation_angle=RotationAngle.RAD90,
    ).draw(axes=ax)
    BlockGate(
        pivot=Vec2D(-0.75, 2.75),
        height=0.5,
        alignment=TransformAlignment.MID_LEFT,
        gate_type=GateType.H,
    ).draw(axes=ax)

    HorizontalVariableIndicator(
        pivot=Vec2D(1.0, 1.25),
        width=0.95,
        height=0.5,
        alignment=TransformAlignment.MID_LEFT,
    ).draw(axes=ax)

    ax.set_xlim(-1, 5)
    ax.set_ylim(0, 4)

    return fig, ax


def plot_debug_schedule(**kwargs) -> IFigureAxesPair:
    # Data allocation
    kwargs[SubplotKeywordEnum.AXES_FORMAT.value] = CircuitAxesFormat()
    kwargs[SubplotKeywordEnum.FIGURE_SIZE.value] = (12, 6)
    fig, ax = construct_subplot(**kwargs)

    fixed_height: float = 0.5

    transform: ChannelBar = ChannelBar(
        pivot=Vec2D(x=4, y=2),
        width=8,
        height=fixed_height,
    )
    transform.draw(axes=ax)
    ax = draw_transform_component(transform, axes=ax)

    header_transform: ChannelHeader = ChannelHeader(
        pivot=transform.rectilinear_transform.pivot,
        height=DynamicLength(lambda: transform.rectilinear_transform.height),
        channel_name='# X1',
        state_description=r'$|0\rangle$'
    )
    header_transform.draw(axes=ax)
    ax = draw_transform_component(header_transform, axes=ax)

    for channel_name, state_desc, pivot in zip(['D1', 'D2', 'D3'], [r'$|+\rangle$', r'$|0\rangle$', r'$|1\rangle$'], [Vec2D(x=4, y=3), Vec2D(x=4, y=4), Vec2D(x=4, y=5)]):
        transform: ChannelBar = ChannelBar(
            pivot=pivot,
            width=8,
            height=0.5,
        )
        transform.draw(axes=ax)
        ax = draw_transform_component(transform, axes=ax)

        header_transform: ChannelHeader = ChannelHeader(
            pivot=transform.rectilinear_transform.pivot,
            height=DynamicLength(lambda: transform.rectilinear_transform.height),
            channel_name=channel_name,
            state_description=state_desc,
        )
        header_transform.draw(axes=ax)
        ax = draw_transform_component(header_transform, axes=ax)

        gate_transform: BlockGate = BlockGate(
            pivot=pivot,
            height=transform.rectilinear_transform.height,
            alignment=TransformAlignment.MID_LEFT,
            gate_type=GateType.H,
        )
        gate_transform.draw(axes=ax)
        ax = draw_transform_component(gate_transform, axes=ax)

    measure_transform: BlockMeasure = BlockMeasure(
        pivot=transform.rectilinear_transform.pivot + Vec2D(x=2, y=0),
        width=2.0,
        height=transform.rectilinear_transform.height,
        alignment=TransformAlignment.MID_LEFT,
    )
    measure_transform.draw(axes=ax)
    ax = draw_transform_component(measure_transform, axes=ax)

    cz_gate_transform: BlockTwoQubitGate = BlockTwoQubitGate(
        main_pivot=FixedPivot(Vec2D(x=5, y=4)),
        vertical_pivot=FixedPivot(Vec2D(x=5.2, y=3)),
        single_block_height=FixedLength(fixed_height),
        single_block_width=FixedLength(fixed_height),
    )
    cz_gate_transform.draw(axes=ax)
    ax = draw_transform_object(cz_gate_transform.rectilinear_transform, axes=ax)
    ax = draw_transform_object(cz_gate_transform.main_transform_block, axes=ax)
    ax = draw_transform_object(cz_gate_transform.second_transform_block, axes=ax)

    ax.set_xlim(-1, 9)
    ax.set_ylim(0, 6)

    return fig, ax


def plot_circuit(circuit: IDeclarativeCircuit, channel_order: List[int] = None, channel_map: Optional[Dict[int, str]] = None, compact_visualization: bool = True, **kwargs) -> IFigureAxesPair:
    if compact_visualization:
        with temporary_override_get_registry_at(VISUALIZATION_DURATION_REGISTRY):
            with clear_lru_cache(RelationLink.get_start_time):
                fig, ax = plot_circuit_description(
                    description=construct_visual_description(
                        circuit=circuit,
                        custom_channel_order=channel_order,
                        custom_channel_map=channel_map,
                    ),
                    **kwargs
                )
        return fig, ax
    # Else
    fig, ax = plot_circuit_description(
        description=construct_visual_description(
            circuit=circuit,
            custom_channel_order=channel_order,
            custom_channel_map=channel_map,
        ),
        **kwargs
    )
    return fig, ax


def plot_circuit_description(description: VisualCircuitDescription, **kwargs) -> IFigureAxesPair:
    # Data allocation
    kwargs[SubplotKeywordEnum.AXES_FORMAT.value] = CircuitAxesFormat()
    kwargs[SubplotKeywordEnum.LABEL_FORMAT.value] = LabelFormat(x_label='', y_label='')
    kwargs[SubplotKeywordEnum.FIGURE_SIZE.value] = kwargs.get(SubplotKeywordEnum.FIGURE_SIZE.value, description.figure_size)
    fig, ax = construct_subplot(**kwargs)

    for i, channel_index in enumerate(description.channel_indices):
        transform: ChannelBar = description.get_channel_bar(index=i)
        transform.draw(axes=ax)
        # ax = draw_transform_component(transform, axes=ax)

        header_transform: ChannelHeader = description.get_channel_header(index=i)
        header_transform.draw(axes=ax)
        # ax = draw_transform_component(header_transform, axes=ax)

    for draw_component in description.get_operation_draw_components():
        draw_component.draw(axes=ax)

    for draw_component in description.get_highlight_draw_components():
        draw_component.draw(axes=ax)

    return fig, ax


if __name__ == '__main__':
    from qce_circuit.language.declarative_circuit import (
        DeclarativeCircuit,
    )
    from qce_circuit.structure.intrf_circuit_operation import (
        ICircuitOperation,
        RelationLink,
        RelationType,
    )
    from qce_circuit.structure.registry_duration import (
        DurationRegistry,
        RegistryDurationStrategy,
    )
    from qce_circuit.structure.registry_repetition import (
        RepetitionRegistry,
        RegistryRepetitionStrategy,
    )

    # Registries
    registry_duration: DurationRegistry = DurationRegistry()
    registry_repetition: RepetitionRegistry = RepetitionRegistry()
    operation_duration_strategy = RegistryDurationStrategy(registry_duration)
    operation_repetition_strategy = RegistryRepetitionStrategy(registry_repetition)

    # Update registries
    registry_duration.set_registry_at(operation_duration_strategy.unique_key, 1.0)  # Dynamic wait duration
    registry_repetition.set_registry_at(operation_repetition_strategy.unique_key, 2)

    circuit: DeclarativeCircuit = DeclarativeCircuit(nr_qubits=2)
    sub_circuit: DeclarativeCircuit = DeclarativeCircuit(
        nr_qubits=2,
        repetition_strategy=operation_repetition_strategy,
    )
    sub_circuit.add(Rx180(
        qubit_index=0,
    ))
    sub_circuit.add(CPhase(
        control_qubit_index=0,
        target_qubit_index=1,
    ))
    sub_circuit.add(Rx180(
        qubit_index=0,
    ))
    sub_circuit.add(Identity(
        qubit_index=1,
        relation=RelationLink(sub_circuit.get_last_entry())
    ))
    sub_circuit.add(Identity(
        qubit_index=1,
    ))
    sub_circuit.add(Identity(
        qubit_index=1,
    ))

    circuit.add(Reset(
        qubit_index=2,
    ))
    circuit.add(Wait(
        qubit_index=2,
        duration_strategy=operation_duration_strategy
    ))
    reference_operation = circuit.get_last_entry()
    sub_circuit._structure.relation_link = RelationLink(reference_operation, RelationType.FOLLOWED_BY)
    circuit.add(sub_circuit._structure)
    circuit.add(DispersiveMeasure(
        qubit_index=2,
        relation=RelationLink(sub_circuit._structure, RelationType.JOINED_END)
    ))
    modified_circuit = circuit.apply_modifiers()

    plot_circuit(circuit=circuit)
    plot_circuit(circuit=modified_circuit)

    plt.show()
