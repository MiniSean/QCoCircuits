# -------------------------------------------
# Module containing functionality for constructing draw components from operation class types.
# -------------------------------------------
from typing import List
from qce_utils.control_interfaces.circuit_definitions.structure.intrf_circuit_operation import (
    ICircuitOperation,
    ChannelIdentifier,
    QubitChannel,
)
from qce_utils.control_interfaces.circuit_definitions.structure.intrf_circuit_operation_composite import (
    ICircuitCompositeOperation,
)
from qce_utils.control_interfaces.circuit_definitions.structure.circuit_operations import (
    CPhase,
    DispersiveMeasure,
    Rx180,
    Rx90,
    Rxm90,
    Ry180,
    Ry90,
    Rym90,
    VirtualPhase,
    Reset,
    Wait,
    Identity,
    Hadamard,
    Barrier,
)
from qce_utils.control_interfaces.circuit_definitions.visualization.intrf_draw_component import IDrawComponent
from qce_utils.control_interfaces.circuit_definitions.visualization.intrf_factory_draw_components import (
    IOperationDrawComponentFactory,
    ITransformConstructor,
)
from qce_utils.support_classes.geometric_definitions.intrf_rectilinear_transform import (
    IRectTransform,
    IPivotStrategy,
    DynamicLength,
    DynamicPivot,
)
from qce_utils.control_interfaces.circuit_definitions.visualization.operation_components import (
    RectangleTextBlock,
    BlockRotation,
    BlockMeasure,
    RotationAxis,
    RotationAngle,
)
from qce_utils.control_interfaces.circuit_definitions.visualization.multi_pivot_components import (
    BlockTwoQubitGate,
    BlockVerticalBarrier,
)
from qce_utils.control_interfaces.circuit_definitions.visualization.annotation_components import (
    HorizontalVariableIndicator,
    RoundedRectangleHighlight,
)


class DefaultFactory(IOperationDrawComponentFactory):

    # region Interface Methods
    def construct(self, operation: ICircuitOperation, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transform: IRectTransform = transform_constructor.construct_transform(
            identifier=operation.channel_identifiers[0],
            time_component=operation,
        )
        return RectangleTextBlock(
            pivot=transform.pivot,
            width=transform.width,
            height=transform.height,
            alignment=transform.parent_alignment,
            text_string=rf'$\mathtt{{?}}$',
        )
    # endregion


class ResetFactory(IOperationDrawComponentFactory):

    # region Interface Methods
    def construct(self, operation: Reset, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transform: IRectTransform = transform_constructor.construct_transform(
            identifier=operation.channel_identifiers[0],
            time_component=operation,
        )
        return RectangleTextBlock(
            pivot=transform.pivot,
            width=transform.width,
            height=transform.height,
            alignment=transform.parent_alignment,
            text_string=rf'$\mathtt{{Reset}}$',
        )
    # endregion


class Rx180Factory(IOperationDrawComponentFactory):

    # region Interface Methods
    def construct(self, operation: Rx180, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transform: IRectTransform = transform_constructor.construct_transform(
            identifier=operation.channel_identifiers[0],
            time_component=operation,
        )
        return BlockRotation(
            pivot=transform.pivot,
            height=transform.height,
            alignment=transform.parent_alignment,
            rotation_axes=RotationAxis.X,
            rotation_angle=RotationAngle.RAD180,
        )
    # endregion


class Rx90Factory(IOperationDrawComponentFactory):

    # region Interface Methods
    def construct(self, operation: Rx90, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transform: IRectTransform = transform_constructor.construct_transform(
            identifier=operation.channel_identifiers[0],
            time_component=operation,
        )
        return BlockRotation(
            pivot=transform.pivot,
            height=transform.height,
            alignment=transform.parent_alignment,
            rotation_axes=RotationAxis.X,
            rotation_angle=RotationAngle.RAD90,
        )
    # endregion


class Rxm90Factory(IOperationDrawComponentFactory):

    # region Interface Methods
    def construct(self, operation: Rxm90, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transform: IRectTransform = transform_constructor.construct_transform(
            identifier=operation.channel_identifiers[0],
            time_component=operation,
        )
        return BlockRotation(
            pivot=transform.pivot,
            height=transform.height,
            alignment=transform.parent_alignment,
            rotation_axes=RotationAxis.X,
            rotation_angle=RotationAngle.RAD90M,
        )
    # endregion


class Ry180Factory(IOperationDrawComponentFactory):

    # region Interface Methods
    def construct(self, operation: Ry180, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transform: IRectTransform = transform_constructor.construct_transform(
            identifier=operation.channel_identifiers[0],
            time_component=operation,
        )
        return BlockRotation(
            pivot=transform.pivot,
            height=transform.height,
            alignment=transform.parent_alignment,
            rotation_axes=RotationAxis.Y,
            rotation_angle=RotationAngle.RAD180,
        )
    # endregion


class Ry90Factory(IOperationDrawComponentFactory):

    # region Interface Methods
    def construct(self, operation: Ry90, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transform: IRectTransform = transform_constructor.construct_transform(
            identifier=operation.channel_identifiers[0],
            time_component=operation,
        )
        return BlockRotation(
            pivot=transform.pivot,
            height=transform.height,
            alignment=transform.parent_alignment,
            rotation_axes=RotationAxis.Y,
            rotation_angle=RotationAngle.RAD90,
        )
    # endregion


class Rym90Factory(IOperationDrawComponentFactory):

    # region Interface Methods
    def construct(self, operation: Rym90, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transform: IRectTransform = transform_constructor.construct_transform(
            identifier=operation.channel_identifiers[0],
            time_component=operation,
        )
        return BlockRotation(
            pivot=transform.pivot,
            height=transform.height,
            alignment=transform.parent_alignment,
            rotation_axes=RotationAxis.Y,
            rotation_angle=RotationAngle.RAD90M,
        )
    # endregion


class ZPhaseFactory(IOperationDrawComponentFactory):

    # region Interface Methods
    def construct(self, operation: VirtualPhase, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transform: IRectTransform = transform_constructor.construct_transform(
            identifier=operation.channel_identifiers[0],
            time_component=operation,
        )
        return BlockRotation(
            pivot=transform.pivot,
            height=transform.height,
            alignment=transform.parent_alignment,
            rotation_axes=RotationAxis.Z,
            rotation_angle=RotationAngle.THETA,
        )
    # endregion


class Rphi90Factory(IOperationDrawComponentFactory):

    # region Interface Methods
    def construct(self, operation: VirtualPhase, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transform: IRectTransform = transform_constructor.construct_transform(
            identifier=operation.channel_identifiers[0],
            time_component=operation,
        )
        return BlockRotation(
            pivot=transform.pivot,
            height=transform.height,
            alignment=transform.parent_alignment,
            rotation_axes=RotationAxis.PHI,
            rotation_angle=RotationAngle.RAD90,
        )
    # endregion


class IdentityFactory(IOperationDrawComponentFactory):

    # region Interface Methods
    def construct(self, operation: Identity, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transform: IRectTransform = transform_constructor.construct_transform(
            identifier=operation.channel_identifiers[0],
            time_component=operation,
        )
        return RectangleTextBlock(
            pivot=transform.pivot,
            width=transform.width,
            height=transform.height,
            alignment=transform.parent_alignment,
            text_string=rf'$\mathtt{{I}}$',
        )
    # endregion


class HadamardFactory(IOperationDrawComponentFactory):

    # region Interface Methods
    def construct(self, operation: Hadamard, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transform: IRectTransform = transform_constructor.construct_transform(
            identifier=operation.channel_identifiers[0],
            time_component=operation,
        )
        return RectangleTextBlock(
            pivot=transform.pivot,
            width=transform.width,
            height=transform.height,
            alignment=transform.parent_alignment,
            text_string=rf'$\mathtt{{H}}$',
        )
    # endregion


class MeasureFactory(IOperationDrawComponentFactory):

    # region Interface Methods
    def construct(self, operation: DispersiveMeasure, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transform: IRectTransform = transform_constructor.construct_transform(
            identifier=operation.channel_identifiers[0],
            time_component=operation,
        )
        return BlockMeasure(
            pivot=transform.pivot,
            width=transform.width,
            height=transform.height,
            alignment=transform.parent_alignment,
        )
    # endregion


class WaitFactory(IOperationDrawComponentFactory):

    # region Interface Methods
    def construct(self, operation: Wait, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transform: IRectTransform = transform_constructor.construct_transform(
            identifier=operation.channel_identifiers[0],
            time_component=operation,
        )
        return HorizontalVariableIndicator(
            pivot=transform.pivot,
            width=transform.width,
            height=transform.height,
            alignment=transform.parent_alignment,
            text_string=r'$\delta$',
        )
    # endregion


class TwoQubitBlockFactory(IOperationDrawComponentFactory):

    # region Interface Methods
    def construct(self, operation: CPhase, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        main_transform: IRectTransform = transform_constructor.construct_transform(
            identifier=ChannelIdentifier(_id=operation.control_qubit_index, _channel=QubitChannel.FLUX),
            time_component=operation,
        )
        second_transform: IRectTransform = transform_constructor.construct_transform(
            identifier=ChannelIdentifier(_id=operation.target_qubit_index, _channel=QubitChannel.FLUX),
            time_component=operation,
        )
        return BlockTwoQubitGate(
            main_pivot=DynamicPivot(lambda: main_transform.pivot),
            vertical_pivot=DynamicPivot(lambda: second_transform.pivot),
            single_block_height=DynamicLength(lambda: main_transform.height),
            single_block_width=DynamicLength(lambda: main_transform.width),
            alignment=main_transform.parent_alignment,
        )
    # endregion


class BarrierFactory(IOperationDrawComponentFactory):

    # region Interface Methods
    def construct(self, operation: Barrier, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transforms: List[IRectTransform] = [
            transform_constructor.construct_transform(
                identifier=ChannelIdentifier(_id=qubit_index, _channel=QubitChannel.ALL),
                time_component=operation,
            )
            for qubit_index in operation.qubit_indices
        ]
        return BlockVerticalBarrier(
            multiple_transforms=transforms,
        )
    # endregion


class FootprintFactory(IOperationDrawComponentFactory):

    # region Interface Methods
    def construct(self, operation: ICircuitCompositeOperation, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transforms: List[IRectTransform] = [
            transform_constructor.construct_transform(
                identifier=channel_identifier,
                time_component=operation,
            )
            for channel_identifier in operation.channel_identifiers
        ]
        transform: IRectTransform = transform_constructor.combine_transforms(transforms=transforms)
        return RoundedRectangleHighlight(
            pivot=transform.pivot,
            width=transform.width,
            height=transform.height,
            alignment=transform.parent_alignment,
            text_string=f'x{operation.nr_of_repetitions}'
        )
    # endregion
