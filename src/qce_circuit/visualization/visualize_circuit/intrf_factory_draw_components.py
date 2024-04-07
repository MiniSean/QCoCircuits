# -------------------------------------------
# Module containing factory interface for converting operation to draw-component.
# Contains factory manager implementation.
# -------------------------------------------
from abc import ABC, abstractmethod, ABCMeta
from dataclasses import dataclass, field
from typing import Type, Dict, List, Generic
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException
from qce_circuit.utilities.intrf_factory_manager import IFactoryManager
from qce_circuit.structure.intrf_circuit_operation import (
    ICircuitOperation,
    TCircuitOperation,
    IDurationComponent,
    ChannelIdentifier,
)
from qce_circuit.utilities.geometric_definitions import (
    IRectTransform,
    TransformAlignment,
    RectTransform,
    Vec2D,
    FixedLength,
    FixedPivot,
)
from qce_circuit.visualization.visualize_circuit.intrf_draw_component import (
    IDrawComponent,
    TDrawComponent,
)


class ITransformConstructor(ABC):
    """
    Interface class, describing conversion methods for constructing IRectTransform from inputs
    """

    # region Interface Methods
    @abstractmethod
    def identifier_to_pivot(self, identifier: ChannelIdentifier, time_component: IDurationComponent) -> Vec2D:
        """:return: Pivot based on channel identifier and duration component."""
        raise InterfaceMethodException

    @abstractmethod
    def identifier_to_width(self, time_component: IDurationComponent) -> float:
        """:return: Rectilinear transform height based on duration component."""
        raise InterfaceMethodException

    @abstractmethod
    def identifier_to_height(self, identifier: ChannelIdentifier) -> float:
        """:return: Rectilinear transform height based on channel identifier."""
        raise InterfaceMethodException

    def construct_transform(self, identifier: ChannelIdentifier, time_component: IDurationComponent) -> IRectTransform:
        """:return: Rectilinear transform based on channel identifier and duration component."""
        return RectTransform(
            _pivot_strategy=FixedPivot(self.identifier_to_pivot(identifier, time_component)),
            _width_strategy=FixedLength(self.identifier_to_width(time_component)),
            _height_strategy=FixedLength(self.identifier_to_height(identifier)),
            _parent_alignment=TransformAlignment.MID_LEFT,
        )

    @classmethod
    def combine_transforms(cls, transforms: List[IRectTransform]) -> IRectTransform:
        """:return: Rectilinear transform that covers all provided transforms."""
        origin_pivots: List[Vec2D] = [transform.origin_pivot for transform in transforms]
        origin_opposite_pivots: List[Vec2D] = [transform.origin_opposite_pivot for transform in transforms]
        combined_origin_pivot: Vec2D = Vec2D(
            x=min([pivot.x for pivot in origin_pivots]),
            y=min([pivot.y for pivot in origin_pivots]),
        )
        combined_origin_opposite_pivot: Vec2D = Vec2D(
            x=max([pivot.x for pivot in origin_opposite_pivots]),
            y=max([pivot.y for pivot in origin_opposite_pivots]),
        )
        return RectTransform(
            _pivot_strategy=FixedPivot(combined_origin_pivot),
            _width_strategy=FixedLength(combined_origin_opposite_pivot.x - combined_origin_pivot.x),
            _height_strategy=FixedLength(combined_origin_opposite_pivot.y - combined_origin_pivot.y),
            _parent_alignment=TransformAlignment.BOT_LEFT,
        )
    # endregion


class IOperationDrawComponentFactory(ABC, Generic[TCircuitOperation, TDrawComponent]):
    """
    Interface class, describing methods for constructing draw-components from operation class types.
    """

    # region Interface Methods
    @abstractmethod
    def construct(self, operation: TCircuitOperation, transform_constructor: ITransformConstructor) -> TDrawComponent:
        """:return: Draw component based on operation type."""
        raise InterfaceMethodException
    # endregion


class IOperationBulkDrawComponentFactory(ABC, Generic[TCircuitOperation, TDrawComponent]):
    """
    Interface class, describing methods for constructing multiple draw-components from multiple operations.
    """

    # region Interface Methods
    @abstractmethod
    def construct(self, operations: List[TCircuitOperation], transform_constructor: ITransformConstructor) -> List[TDrawComponent]:
        """:return: Draw components based on array-like of operations."""
        raise InterfaceMethodException
    # endregion


class IOperationDrawComponentFactoryManager(IOperationDrawComponentFactory, IFactoryManager[Type[ICircuitOperation]], metaclass=ABCMeta):
    """
    Interface class, describing factory manager for operation draw-components.
    """


class IOperationBulkDrawComponentFactoryManager(IOperationBulkDrawComponentFactory, IFactoryManager[Type[ICircuitOperation]], metaclass=ABCMeta):
    """
    Interface class, describing factory manager for (bulk) operation draw-components.
    """


@dataclass(frozen=True)
class DrawComponentFactoryManager(IOperationDrawComponentFactoryManager):
    """
    Behaviour class, implementing operation to draw-component construction based on factory-lookup
    """
    default_factory: IOperationDrawComponentFactory
    """Factory that constructs component independent of operation-type."""
    factory_lookup: Dict[Type[ICircuitOperation], IOperationDrawComponentFactory] = field(default_factory=dict)
    """Lookup that maps operation-type to draw-component factory."""

    # region Interface Properties
    @property
    def supported_factories(self) -> List[Type[ICircuitOperation]]:
        """:return: Array-like of supported factory types."""
        return list(set(self.factory_lookup.keys()))
    # endregion

    # region Interface Methods
    def construct(self, operation: ICircuitOperation, transform_constructor: ITransformConstructor) -> IDrawComponent:
        """:return: Draw component based on operation type."""
        # Guard clause, if request not supported raise exception
        operation_supported: bool = type(operation) in self.factory_lookup
        if not operation_supported:
            # raise FactoryManagerKeyException(f"Operation of type {type(operation)} is not supported in {list(self.factory_lookup.keys())}.")
            return self.default_factory.construct(operation=operation, transform_constructor=transform_constructor)

        return self.factory_lookup[type(operation)].construct(operation=operation, transform_constructor=transform_constructor)

    def contains(self, factory_key: Type[ICircuitOperation]) -> bool:
        """:return: Boolean, whether factory key is included in the manager."""
        return factory_key in self.supported_factories
    # endregion


@dataclass(frozen=True)
class BulkDrawComponentFactoryManager(IOperationBulkDrawComponentFactoryManager):
    """
    Behaviour class, implementing operation to draw-component construction based on factory-lookup
    """
    individual_component_factory: IOperationDrawComponentFactoryManager
    """Factory that constructs component independent of operation-type."""
    factory_lookup: Dict[Type[ICircuitOperation], IOperationBulkDrawComponentFactory] = field(default_factory=dict)
    """Lookup that maps operation-type to draw-component factory."""

    # region Interface Properties
    @property
    def supported_factories(self) -> List[Type[ICircuitOperation]]:
        """:return: Array-like of supported factory types."""
        return list(set(self.factory_lookup.keys()))
    # endregion

    # region Interface Methods
    def construct(self, operations: List[ICircuitOperation], transform_constructor: ITransformConstructor) -> List[IDrawComponent]:
        """:return: Draw components based on array-like of operations."""
        result: List[IDrawComponent] = []
        operation_lookup: Dict[Type[ICircuitOperation], List[ICircuitOperation]] = {}

        # Group operations based on their type
        for operation in operations:
            operation_type = type(operation)
            if operation_type not in operation_lookup:
                operation_lookup[operation_type] = [operation]
            else:
                operation_lookup[operation_type].append(operation)

        # Iterate over all (type) groups of operations and process them either by default factory or factory lookup
        for _type, _operations in operation_lookup.items():
            # Guard clause, if request not supported raise exception
            operation_supported: bool = _type in self.factory_lookup

            if not operation_supported:
                for _operation in _operations:
                    result.append(self.individual_component_factory.construct(
                        operation=_operation,
                        transform_constructor=transform_constructor,
                    ))
                continue

            result.extend(self.factory_lookup[_type].construct(
                operations=_operations,
                transform_constructor=transform_constructor,
            ))

        return result

    def contains(self, factory_key: Type[ICircuitOperation]) -> bool:
        """:return: Boolean, whether factory key is included in the manager."""
        return factory_key in self.supported_factories
    # endregion
