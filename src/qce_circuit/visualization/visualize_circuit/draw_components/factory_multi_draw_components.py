# -------------------------------------------
# Module containing functionality for constructing multiple draw components from multiple operation class types.
# Mainly intended to deal with (two-qubit gate) overlapping draw components.
# -------------------------------------------
from typing import List, Generic, Dict, Tuple, TypeVar, Type
from dataclasses import dataclass, field
from qce_circuit.structure.intrf_circuit_operation import TCircuitOperation, ChannelIdentifier, QubitChannel
from qce_circuit.structure.circuit_operations import CPhase, TwoQubitOperation
from qce_circuit.visualization.visualize_circuit.draw_components.factory_draw_components import TwoQubitBlockFactory
from qce_circuit.visualization.visualize_circuit.draw_components.transform_constructor import OffsetTransformConstructor
from qce_circuit.visualization.visualize_circuit.intrf_draw_component import IDrawComponent
from qce_circuit.visualization.visualize_circuit.intrf_factory_draw_components import (
    IOperationDrawComponentFactory,
    IOperationBulkDrawComponentFactory,
    ITransformConstructor,
)
from qce_circuit.utilities.geometric_definitions import (
    IRectTransform,
)


TCircuitTwoQubitOperation = TypeVar('TCircuitTwoQubitOperation', bound=TwoQubitOperation)


@dataclass(frozen=True)
class GroupedOperationIdentifier(Generic[TCircuitOperation]):
    operation: TCircuitOperation
    """Operation element."""
    transform: IRectTransform
    """Operation transform."""
    group_index: int
    """Integer ID for group."""
    group_size: int
    """Integer number of elements in group."""
    element_index: int
    """Integer ID for operation in group (0 <= element_id < group_size)."""


@dataclass(frozen=True)
class SpaceSharedOperations(Generic[TCircuitOperation]):
    """
    Data class, describing space-shared operations (rect-transform)
    """
    operations: List[GroupedOperationIdentifier[TCircuitOperation]]

    # region Class Properties
    @property
    def group_id(self) -> int:
        return self.operations[0].group_index

    @property
    def group_size(self) -> int:
        return self.operations[0].group_size
    # endregion

    # region Class Methods
    def __post_init__(self):
        group_sizes = [operation.group_size for operation in self.operations]
        group_ids = [operation.group_index for operation in self.operations]
        element_ids = [operation.element_index for operation in self.operations]
        assert len(set(group_sizes)) == 1, f"Expects all operations to indicate the same group-size. Instead {group_sizes}"
        assert len(set(group_ids)) == 1, f"Expects all operations to indicate the same group-ID. Instead {group_ids}"
        assert len(set(element_ids)) == len(self.operations), f"Expects all operations to indicate unique element-ID. Instead {element_ids}"

    @classmethod
    def divide(cls, operations: List[TCircuitTwoQubitOperation], transform_constructor: ITransformConstructor) -> List['SpaceSharedOperations[TCircuitTwoQubitOperation]']:
        """
        Construct rect-transforms for each operation based on draw-factory and transform-constructor.
        Sort rect-transforms based on Y-starting coordinate (MID-BOTTOM).

        :return: Array-like of space-shared operations.
        """
        # Guard clause, if operations is an empty list, return empty list
        if len(operations) == 0:
            return []
        operation_to_transform: Dict[TCircuitTwoQubitOperation, IRectTransform] = {
            operation: transform_constructor.combine_transforms(transforms=[
                transform_constructor.construct_transform(
                    identifier=ChannelIdentifier(_id=operation.control_qubit_index, _channel=QubitChannel.ALL),
                    time_component=operation,
                ),
                transform_constructor.construct_transform(
                    identifier=ChannelIdentifier(_id=operation.target_qubit_index, _channel=QubitChannel.ALL),
                    time_component=operation,
                )
            ])
            for operation in operations
        }
        increasing_y_coord: List[TCircuitTwoQubitOperation] = sorted(operations, key=lambda x: operation_to_transform[x].bot_pivot.y)
        # Store grouped operations
        grouped_operations: List[List[TCircuitTwoQubitOperation]] = []
        # Store y-bound per group index
        group_y_bound_lookup: Dict[int, Tuple[float, float]] = {}

        for operation in increasing_y_coord:
            transform: IRectTransform = operation_to_transform[operation]
            group_index: int = len(group_y_bound_lookup)  # Default to new group index

            # Guard clause, first entry
            if len(grouped_operations) == 0:
                grouped_operations.append([operation])
                group_y_bound_lookup[group_index] = (transform.bot_pivot.y, transform.top_pivot.y)
                continue

            # Evaluate group index
            for _group_index in group_y_bound_lookup.keys():
                y_lower_bound, y_upper_bound = group_y_bound_lookup[_group_index]
                included_in_group: bool = transform.bot_pivot.y <= y_upper_bound
                if included_in_group:
                    group_index = _group_index
                    continue

            extend_existing_group: bool = group_index in group_y_bound_lookup
            # Extend existing group
            if extend_existing_group:
                grouped_operations[group_index].append(operation)
                y_lower_bound, y_upper_bound = group_y_bound_lookup[group_index]
                group_y_bound_lookup[group_index] = (y_lower_bound, transform.top_pivot.y)
            else:  # Add new group
                grouped_operations.append([operation])
                group_y_bound_lookup[group_index] = (transform.bot_pivot.y, transform.top_pivot.y)

        return [
            SpaceSharedOperations(
                operations=[
                    GroupedOperationIdentifier(
                        operation=operation,
                        transform=operation_to_transform[operation],
                        group_index=i,
                        group_size=len(space_shared_operations),
                        element_index=j,
                    )
                    for j, operation in enumerate(space_shared_operations)
                ]
            )
            for i, space_shared_operations in enumerate(grouped_operations)
        ]
    # endregion


@dataclass(frozen=True)
class TimeSharedOperations(Generic[TCircuitOperation]):
    """
    Data class, describing time-shared operations
    """
    operations: List[TCircuitOperation]

    # region Class Properties
    @property
    def shared_start_time(self) -> float:
        return self.operations[0].start_time
    # endregion

    # region Class Methods
    @classmethod
    def divide(cls, operations: List[TCircuitOperation]) -> List['TimeSharedOperations[TCircuitOperation]']:
        """:return: Array-like of time-shared operations."""
        # Guard clause, if operations is an empty list, return empty list
        if len(operations) == 0:
            return []
        time_lookup: Dict[float, List[TCircuitOperation]] = {}
        for operation in operations:
            operation_start_time: float = operation.start_time
            if operation_start_time not in time_lookup:
                time_lookup[operation_start_time] = [operation]
            else:
                time_lookup[operation_start_time].append(operation)

        return [
            TimeSharedOperations(
                operations=time_shared_operations,
            )
            for time_shared_operations in time_lookup.values()
        ]
    # endregion


@dataclass(frozen=True)
class MultiTwoQubitBlockFactory(IOperationBulkDrawComponentFactory[TCircuitTwoQubitOperation, IDrawComponent]):
    factory_lookup: Dict[Type[TCircuitTwoQubitOperation], IOperationDrawComponentFactory] = field(default_factory=dict)

    # region Interface Methods
    def construct(self, operations: List[TCircuitTwoQubitOperation], transform_constructor: ITransformConstructor) -> List[IDrawComponent]:
        """:return: Draw components based on array-like of operations."""
        result: List[IDrawComponent] = []
        scalar: float = 0.5  # Make sure operation is still displayed within original duration by 50%

        # Debugging
        time_shared_groups: List[TimeSharedOperations] = TimeSharedOperations.divide(operations=operations)
        for time_group in time_shared_groups:

            space_shared_groups: List[SpaceSharedOperations] = SpaceSharedOperations.divide(
                operations=time_group.operations,
                transform_constructor=transform_constructor
            )
            for space_group in space_shared_groups:
                for operation in space_group.operations:
                    # Guard clause, operation not in lookup, continue
                    if type(operation.operation) not in self.factory_lookup:
                        continue

                    individual_factory: IOperationDrawComponentFactory = self.factory_lookup[type(operation.operation)]

                    # Guard clause, if group size is one, treat normally
                    if operation.group_size == 1:
                        result.append(individual_factory.construct(
                            operation=operation.operation,
                            transform_constructor=transform_constructor,
                        ))
                        continue

                    bounded_offset: float = (2 * (operation.element_index / (operation.group_size - 1)) - 1.0)  # [-1, +1]
                    duration_scaling: float = 0.5 * operation.operation.duration  # tau / 2
                    offset_scalar: float = bounded_offset * duration_scaling * scalar
                    offset_transform_constructor: ITransformConstructor = OffsetTransformConstructor(
                        default_transform=transform_constructor,
                        pivot_offset_scalar_x=offset_scalar,
                    )
                    result.append(individual_factory.construct(
                        operation=operation.operation,
                        transform_constructor=offset_transform_constructor,
                    ))

        return result
    # endregion
