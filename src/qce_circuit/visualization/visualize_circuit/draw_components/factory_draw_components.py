# -------------------------------------------
# Module containing functionality for constructing draw components from operation class types.
# -------------------------------------------
from dataclasses import dataclass, field
from typing import List
from qce_circuit.structure.intrf_circuit_operation import (
    ICircuitOperation,
    ChannelIdentifier,
    QubitChannel,
)
from qce_circuit.structure.intrf_circuit_operation_composite import (
    ICircuitCompositeOperation,
)
from qce_circuit.structure.circuit_operations import (
    CPhase,
    DispersiveMeasure,
    Rx180,
    Rx90,
    Rxm90,
    RxTheta,
    Ry180,
    Ry90,
    Rym90,
    RyTheta,
    VirtualPhase,
    Reset,
    Wait,
    Identity,
    Hadamard,
    Barrier,
    VirtualPark,
    VirtualVacant,
    VirtualTwoQubitVacant,
    VirtualEmpty,
    VirtualOptional,
    VirtualInjectedError,
    VirtualWait,
    VirtualColorOverwrite,
)
from qce_circuit.visualization.visualize_circuit.intrf_draw_component import IDrawComponent
from qce_circuit.visualization.visualize_circuit.intrf_factory_draw_components import (
    IOperationDrawComponentFactoryManager,
    IOperationDrawComponentFactory,
    ITransformConstructor,
)
from qce_circuit.utilities.geometric_definitions.intrf_rectilinear_transform import (
    IRectTransform,
    DynamicLength,
    DynamicPivot,
)
from qce_circuit.visualization.visualize_circuit.draw_components.operation_components import (
    RectangleBlock,
    RectangleTextBlock,
    RectangleVacantBlock,
    BlockRotation,
    BlockHeaderBody,
    BlockMeasure,
    RotationAxis,
    RotationAngle,
    SquareParkBlock,
    SquareNetZeroParkBlock,
)
from qce_circuit.visualization.visualize_circuit.draw_components.multi_pivot_components import (
    BlockTwoQubitGate,
    BlockVerticalBarrier,
    BlockTwoQubitVacant,
)
from qce_circuit.visualization.visualize_circuit.draw_components.annotation_components import (
    HorizontalVariableIndicator,
    RoundedRectangleHighlight,
)
from qce_circuit.visualization.visualize_circuit.style_manager import StyleManager


class DefaultFactory(IOperationDrawComponentFactory[ICircuitOperation, IDrawComponent]):

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


class ResetFactory(IOperationDrawComponentFactory[Reset, IDrawComponent]):

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


@dataclass(frozen=True)
class Rx180Factory(IOperationDrawComponentFactory[Rx180, IDrawComponent]):
    minimalist: bool = field(default=False)

    # region Interface Methods
    def construct(self, operation: Rx180, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transform: IRectTransform = transform_constructor.construct_transform(
            identifier=operation.channel_identifiers[0],
            time_component=operation,
        )
        if self.minimalist:
            return BlockHeaderBody(
                pivot=transform.pivot,
                height=transform.height,
                alignment=transform.parent_alignment,
                header_text=f"{RotationAxis.X.value}",
            )

        return BlockRotation(
            pivot=transform.pivot,
            height=transform.height,
            alignment=transform.parent_alignment,
            rotation_axes=RotationAxis.X,
            rotation_angle=RotationAngle.RAD180,
        )
    # endregion


@dataclass(frozen=True)
class Rx90Factory(IOperationDrawComponentFactory[Rx90, IDrawComponent]):
    minimalist: bool = field(default=False)

    # region Interface Methods
    def construct(self, operation: Rx90, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transform: IRectTransform = transform_constructor.construct_transform(
            identifier=operation.channel_identifiers[0],
            time_component=operation,
        )
        if self.minimalist:
            return BlockHeaderBody(
                pivot=transform.pivot,
                height=transform.height,
                alignment=transform.parent_alignment,
                header_text=f"+{RotationAxis.X.value}/2",
            )

        return BlockRotation(
            pivot=transform.pivot,
            height=transform.height,
            alignment=transform.parent_alignment,
            rotation_axes=RotationAxis.X,
            rotation_angle=RotationAngle.RAD90,
        )
    # endregion


@dataclass(frozen=True)
class Rxm90Factory(IOperationDrawComponentFactory[Rxm90, IDrawComponent]):
    minimalist: bool = field(default=False)

    # region Interface Methods
    def construct(self, operation: Rxm90, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transform: IRectTransform = transform_constructor.construct_transform(
            identifier=operation.channel_identifiers[0],
            time_component=operation,
        )
        if self.minimalist:
            return BlockHeaderBody(
                pivot=transform.pivot,
                height=transform.height,
                alignment=transform.parent_alignment,
                header_text=f"-{RotationAxis.X.value}/2",
            )

        return BlockRotation(
            pivot=transform.pivot,
            height=transform.height,
            alignment=transform.parent_alignment,
            rotation_axes=RotationAxis.X,
            rotation_angle=RotationAngle.RAD90M,
        )
    # endregion


class RxThetaFactory(IOperationDrawComponentFactory[RxTheta, IDrawComponent]):

    # region Interface Methods
    def construct(self, operation: RxTheta, transform_constructor: ITransformConstructor) -> IDrawComponent:
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
            rotation_angle=RotationAngle.THETA,
        )
    # endregion


@dataclass(frozen=True)
class Ry180Factory(IOperationDrawComponentFactory[Ry180, IDrawComponent]):
    minimalist: bool = field(default=False)

    # region Interface Methods
    def construct(self, operation: Ry180, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transform: IRectTransform = transform_constructor.construct_transform(
            identifier=operation.channel_identifiers[0],
            time_component=operation,
        )
        if self.minimalist:
            return BlockHeaderBody(
                pivot=transform.pivot,
                height=transform.height,
                alignment=transform.parent_alignment,
                header_text=f"{RotationAxis.Y.value}",
            )

        return BlockRotation(
            pivot=transform.pivot,
            height=transform.height,
            alignment=transform.parent_alignment,
            rotation_axes=RotationAxis.Y,
            rotation_angle=RotationAngle.RAD180,
        )
    # endregion


@dataclass(frozen=True)
class Ry90Factory(IOperationDrawComponentFactory[Ry90, IDrawComponent]):
    minimalist: bool = field(default=False)

    # region Interface Methods
    def construct(self, operation: Ry90, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transform: IRectTransform = transform_constructor.construct_transform(
            identifier=operation.channel_identifiers[0],
            time_component=operation,
        )
        if self.minimalist:
            return BlockHeaderBody(
                pivot=transform.pivot,
                height=transform.height,
                alignment=transform.parent_alignment,
                header_text=f"+{RotationAxis.Y.value}/2",
            )

        return BlockRotation(
            pivot=transform.pivot,
            height=transform.height,
            alignment=transform.parent_alignment,
            rotation_axes=RotationAxis.Y,
            rotation_angle=RotationAngle.RAD90,
        )
    # endregion


@dataclass(frozen=True)
class Rym90Factory(IOperationDrawComponentFactory[Rym90, IDrawComponent]):
    minimalist: bool = field(default=False)

    # region Interface Methods
    def construct(self, operation: Rym90, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transform: IRectTransform = transform_constructor.construct_transform(
            identifier=operation.channel_identifiers[0],
            time_component=operation,
        )
        if self.minimalist:
            return BlockHeaderBody(
                pivot=transform.pivot,
                height=transform.height,
                alignment=transform.parent_alignment,
                header_text=f"-{RotationAxis.Y.value}/2",
            )

        return BlockRotation(
            pivot=transform.pivot,
            height=transform.height,
            alignment=transform.parent_alignment,
            rotation_axes=RotationAxis.Y,
            rotation_angle=RotationAngle.RAD90M,
        )
    # endregion


class RyThetaFactory(IOperationDrawComponentFactory[RyTheta, IDrawComponent]):

    # region Interface Methods
    def construct(self, operation: RyTheta, transform_constructor: ITransformConstructor) -> IDrawComponent:
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
            rotation_angle=RotationAngle.THETA,
        )
    # endregion


@dataclass(frozen=True)
class Rx180efFactory(IOperationDrawComponentFactory[Rx180, IDrawComponent]):
    minimalist: bool = field(default=False)

    # region Interface Methods
    def construct(self, operation: Rx180, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transform: IRectTransform = transform_constructor.construct_transform(
            identifier=operation.channel_identifiers[0],
            time_component=operation,
        )
        if self.minimalist:
            return BlockHeaderBody(
                pivot=transform.pivot,
                height=transform.height,
                alignment=transform.parent_alignment,
                header_text=f"${RotationAxis.X.value}_{{12}}$",
            )

        return BlockRotation(
            pivot=transform.pivot,
            height=transform.height,
            alignment=transform.parent_alignment,
            rotation_axes=RotationAxis.X_EF,
            rotation_angle=RotationAngle.RAD180,
        )
    # endregion


class ZPhaseFactory(IOperationDrawComponentFactory[VirtualPhase, IDrawComponent]):

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


class Rphi90Factory(IOperationDrawComponentFactory[VirtualPhase, IDrawComponent]):

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


class IdentityFactory(IOperationDrawComponentFactory[Identity, IDrawComponent]):

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


class HadamardFactory(IOperationDrawComponentFactory[Hadamard, IDrawComponent]):

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


class VirtualParkFactory(IOperationDrawComponentFactory[VirtualPark, IDrawComponent]):

    # region Interface Methods
    def construct(self, operation: VirtualPark, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transform: IRectTransform = transform_constructor.construct_transform(
            identifier=operation.channel_identifiers[0],
            time_component=operation,
        )
        if operation.net_zero:
            return SquareNetZeroParkBlock(
                pivot=transform.pivot,
                height=transform.height,
                width=transform.width,
                alignment=transform.parent_alignment,
            )

        return SquareParkBlock(
            pivot=transform.pivot,
            height=transform.height,
            width=transform.width,
            alignment=transform.parent_alignment,
        )
    # endregion


class VirtualVacantFactory(IOperationDrawComponentFactory[VirtualVacant, IDrawComponent]):

    # region Interface Methods
    def construct(self, operation: VirtualVacant, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transform: IRectTransform = transform_constructor.construct_transform(
            identifier=operation.channel_identifiers[0],
            time_component=operation,
        )
        return RectangleVacantBlock(
            pivot=transform.pivot,
            height=transform.height,
            width=transform.width,
            alignment=transform.parent_alignment,
        )
    # endregion


class VirtualTwoQubitVacantFactory(IOperationDrawComponentFactory[VirtualTwoQubitVacant, IDrawComponent]):

    # region Interface Methods
    def construct(self, operation: VirtualTwoQubitVacant, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        main_transform: IRectTransform = transform_constructor.construct_transform(
            identifier=ChannelIdentifier(_id=operation.control_qubit_index, _channel=QubitChannel.FLUX),
            time_component=operation,
        )
        second_transform: IRectTransform = transform_constructor.construct_transform(
            identifier=ChannelIdentifier(_id=operation.target_qubit_index, _channel=QubitChannel.FLUX),
            time_component=operation,
        )
        return BlockTwoQubitVacant(
            main_pivot=DynamicPivot(lambda: main_transform.pivot),
            vertical_pivot=DynamicPivot(lambda: second_transform.pivot),
            single_block_height=DynamicLength(lambda: main_transform.height),
            single_block_width=DynamicLength(lambda: main_transform.width),
            alignment=main_transform.parent_alignment,
        )
    # endregion


class VirtualEmptyFactory(IOperationDrawComponentFactory[VirtualEmpty, IDrawComponent]):

    # region Interface Methods
    def construct(self, operation: VirtualEmpty, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transform: IRectTransform = transform_constructor.construct_transform(
            identifier=operation.channel_identifiers[0],
            time_component=operation,
        )
        return RectangleBlock(
            pivot=transform.pivot,
            height=transform.height,
            width=transform.width,
            alignment=transform.parent_alignment,
            style_settings=StyleManager.read_config().empty_operation_style,
        )
    # endregion


class VirtualWaitFactory(IOperationDrawComponentFactory[VirtualWait, IDrawComponent]):

    # region Interface Methods
    def construct(self, operation: VirtualWait, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        transform: IRectTransform = transform_constructor.construct_transform(
            identifier=operation.channel_identifiers[0],
            time_component=operation,
        )
        return BlockHeaderBody(
            pivot=transform.pivot,
            height=transform.height,
            alignment=transform.parent_alignment,
            header_text=operation.header_text,
            body_text=operation.body_text,
        )
    # endregion


class MeasureFactory(IOperationDrawComponentFactory[DispersiveMeasure, IDrawComponent]):

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


class WaitFactory(IOperationDrawComponentFactory[Wait, IDrawComponent]):

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


class TwoQubitBlockFactory(IOperationDrawComponentFactory[CPhase, IDrawComponent]):

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


class BarrierFactory(IOperationDrawComponentFactory[Barrier, IDrawComponent]):

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


class FootprintFactory(IOperationDrawComponentFactory[ICircuitCompositeOperation, IDrawComponent]):

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


class VirtualOptionalFactory(IOperationDrawComponentFactory[VirtualOptional, IDrawComponent]):
    """
    Behaviour class, implementing construction of draw component with additional requirements.
    """

    # region Class Constructor
    def __init__(self, callback_draw_manager: IOperationDrawComponentFactoryManager):
        self._factory_manager: IOperationDrawComponentFactoryManager = callback_draw_manager
    # endregion

    # region Interface Methods
    def construct(self, operation: VirtualOptional, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        with StyleManager.temporary_override(**dict(line_style_border='--')):
            draw_component: IDrawComponent = self._factory_manager.construct(
                operation=operation.operation,
                transform_constructor=transform_constructor,
            )
        return draw_component
    # endregion


class VirtualInjectedErrorFactory(IOperationDrawComponentFactory[VirtualInjectedError, IDrawComponent]):
    """
    Behaviour class, implementing construction of draw component with additional requirements.
    """

    # region Class Constructor
    def __init__(self, callback_draw_manager: IOperationDrawComponentFactoryManager):
        self._factory_manager: IOperationDrawComponentFactoryManager = callback_draw_manager
    # endregion

    # region Interface Methods
    def construct(self, operation: VirtualInjectedError, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        with StyleManager.temporary_override(**dict(line_style_border='--', color_background="#ff9999")):
            draw_component: IDrawComponent = self._factory_manager.construct(
                operation=operation.operation,
                transform_constructor=transform_constructor,
            )
        return draw_component
    # endregion


class VirtualColorOverwriteFactory(IOperationDrawComponentFactory[VirtualColorOverwrite, IDrawComponent]):
    """
    Behaviour class, implementing construction of draw component with additional requirements.
    """

    # region Class Constructor
    def __init__(self, callback_draw_manager: IOperationDrawComponentFactoryManager):
        self._factory_manager: IOperationDrawComponentFactoryManager = callback_draw_manager
    # endregion

    # region Interface Methods
    def construct(self, operation: VirtualColorOverwrite, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        with StyleManager.temporary_override(**dict(
            color_text=operation.color_overwrite,
            color_icon=operation.color_overwrite,
            color_outline=operation.color_overwrite,
        )):
            draw_component: IDrawComponent = self._factory_manager.construct(
                operation=operation.operation,
                transform_constructor=transform_constructor,
            )
        return draw_component
    # endregion
