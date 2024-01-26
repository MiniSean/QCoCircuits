# -------------------------------------------
# Module describing the declarative circuit structure.
# -------------------------------------------
from abc import abstractmethod, ABCMeta
from dataclasses import dataclass, field
import warnings
from typing import List, Iterator, Optional, Dict
import numpy as np
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException
from qce_circuit.utilities.array_manipulation import unique_in_order
from qce_circuit.structure.intrf_circuit_operation import (
    ICircuitNode,
    IRelationLink,
    RelationLink,
    RelationType,
    MultiRelationLink,
    MultiRelationType,
    ChannelIdentifier,
    ICircuitOperation,
)
from qce_circuit.structure.graph_traversal.intrf_graph_structure import (
    IEndpoint,
    GraphNode,
    GraphBranch,
)
from qce_circuit.structure.registry_repetition import (
    IRepetitionStrategy,
    FixedRepetitionStrategy,
)


@dataclass(frozen=True)
class CircuitNode(ICircuitNode):
    """
    Data class, placeholder.
    """
    pass


@dataclass(frozen=True)
class OperationGraphNode(GraphNode):
    operation: ICircuitOperation

    # region Class Methods
    def __hash__(self):
        # Use the id of the instance for a unique hash
        return id(self)

    def __repr__(self):
        return f"{self.operation.__class__.__name__}-{self.__class__.__name__}(#{str(self.identifier).zfill(3)})"
    # endregion


class CircuitGraphBranch(GraphBranch[OperationGraphNode]):

    # region Class Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Unique array-like of channel identifiers present in graph."""
        identifiers: List[ChannelIdentifier] = []
        for node in self.get_node_iterator():
            identifiers.extend(node.operation.channel_identifiers)
        return unique_in_order(identifiers)
    # endregion

    # region Class Methods
    def append_to(self, endpoint: OperationGraphNode, pointer: OperationGraphNode) -> 'CircuitGraphBranch':
        """:return: Appends self with another entry/end point maintainer."""
        # Append before endpoint
        incoming_pointers: List[IEndpoint] = self._endpoint_node.incoming_pointers
        for incoming_pointer in incoming_pointers:
            if incoming_pointer is endpoint:
                incoming_pointer.release_pointer(pointer=self._endpoint_node)
        endpoint.point_towards(pointer=pointer)
        # Update branch pointers
        self.update_point_leafs_to_endpoint()  # Points all leaf nodes to endpoint
        return self

    def get_node_iterator(self) -> Iterator[OperationGraphNode]:
        """
        :return: Iterator, overwrites super by filtering on OperationGraphNode instances.
        """
        for node in super().get_node_iterator():
            if isinstance(node, OperationGraphNode):
                yield node

    def get_leaf_at_any(self, channel_identifiers: List[ChannelIdentifier]) -> Optional[OperationGraphNode]:
        """
        If not able to find channel identifier in any of the nodes, return None.
        :return: Latest relation node in channel. Defined in relation steps, not in time.
        """
        for node in reversed(list(self.get_node_iterator())):
            any_identifier_corresponds: bool = any(element in node.operation.channel_identifiers for element in channel_identifiers)
            if any_identifier_corresponds:
                return node
        return None

    def get_corresponding_node(self, operation: ICircuitOperation) -> Optional[OperationGraphNode]:
        """
        If not able to find corresponding node, return None.
        :return: OperationGraphNode with corresponding operation. Used for tracking relations.
        """
        for node in self.get_node_iterator():
            if operation is node.operation:
                return node
        return None
    # endregion


class ICircuitCompositeOperation(ICircuitOperation, metaclass=ABCMeta):
    """
    Interface class, describing basic methods and properties to construct circuit.
    """

    # region Interface Methods
    @abstractmethod
    def add(self, operation: ICircuitOperation) -> 'ICircuitCompositeOperation':
        """:return: Self. Adds operation to circuit."""
        raise InterfaceMethodException
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class CircuitCompositeOperation(ICircuitCompositeOperation):
    """
    Data class, describing a relationship-based circuit schedule.
    """
    relation: IRelationLink[ICircuitOperation] = field(init=True, default_factory=RelationLink.no_relation)
    repetition_strategy: IRepetitionStrategy = field(init=True, default=FixedRepetitionStrategy(repetitions=1))
    _circuit_graph: CircuitGraphBranch = field(init=False, default_factory=CircuitGraphBranch)

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return self._circuit_graph.channel_identifiers

    @property
    def nr_of_repetitions(self) -> int:
        """:return: Number of repetitions for this object."""
        return self.repetition_strategy.get_repetition_number(self)

    @property
    def relation_link(self) -> IRelationLink[ICircuitOperation]:
        """:return: Description of relation to other circuit node."""
        return self.relation

    @relation_link.setter
    def relation_link(self, link: IRelationLink[ICircuitOperation]):
        """:sets: Description of relation to other circuit node."""
        self.relation = link

    @property
    def start_time(self) -> float:
        """:return: Start time [a.u.]."""
        return self.relation_link.get_start_time(duration=self.duration)

    @property
    def duration(self) -> float:
        """:return: Duration [ns]."""
        total_duration: float = 0.0
        # Calculate relative start time of internal operations
        relative_start_time: float = +np.inf
        for start_node in self._circuit_graph.get_nodes_at(depth=1):
            if start_node.operation.start_time < relative_start_time:
                relative_start_time = start_node.operation.start_time
        # Calculate internal duration of operation branch
        for leaf_node in self._circuit_graph.leaf_nodes:
            delta_time = leaf_node.operation.end_time - relative_start_time
            if delta_time > total_duration:
                total_duration = delta_time
        return total_duration
    # endregion

    # region Interface Methods
    def add(self, operation: ICircuitOperation) -> ICircuitCompositeOperation:
        """:return: Self. Adds operation to circuit."""
        # Data allocation
        node: OperationGraphNode = OperationGraphNode(operation=operation)
        leaf_node: Optional[OperationGraphNode] = self._circuit_graph.get_leaf_at_any(channel_identifiers=operation.channel_identifiers)
        has_relation: bool = operation.has_relation
        first_in_channel: bool = leaf_node is None

        # Logic
        if not has_relation and first_in_channel:
            self._circuit_graph.append_to(self._circuit_graph.root_node, node)
            return self

        if not has_relation and not first_in_channel:
            node.operation.relation_link = RelationLink(
                _reference_node=leaf_node.operation,
            )
            self._circuit_graph.append_to(leaf_node, node)
            return self

        relation_node: Optional[OperationGraphNode] = self._circuit_graph.get_corresponding_node(operation=node.operation.relation_link.reference_node)
        relation_node_present: bool = relation_node is not None
        if has_relation and relation_node_present:
            self._circuit_graph.append_to(relation_node, node)
            return self

        if has_relation and not relation_node_present:
            warnings.warn(f"Expected operation relation ({node.operation.relation_link.reference_node}) is not present in circuit.")

        return self

    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'CircuitCompositeOperation':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        result = CircuitCompositeOperation(
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
            repetition_strategy=self.repetition_strategy,
        )
        # Used to re-establish relation link
        if relation_transfer_lookup is None:
            relation_transfer_lookup = {}

        # Iterate through nodes and rebuild circuit composite
        for node in self._circuit_graph.get_node_iterator():
            operation_copy = node.operation.copy(relation_transfer_lookup=relation_transfer_lookup)
            # Keep track of copied operations for relation transfer
            relation_transfer_lookup[node.operation] = operation_copy
            result.add(operation_copy)

        return result

    def apply_modifiers_to_self(self) -> ICircuitOperation:
        """
        WARNING: Applies modifiers inplace.
        Applies modifiers such as repetition and state-control.
        :return: Modified self.
        """
        # Apply repetition modifier to self (update strategy)
        self.repeat(times=self.nr_of_repetitions)
        self.repetition_strategy = FixedRepetitionStrategy(repetitions=1)
        for node in self._circuit_graph.get_node_iterator():
            node.operation.apply_modifiers_to_self()

        return self

    def decomposed_operations(self) -> List[ICircuitOperation]:
        """
        Functions similar to a 'flatten' operation.
        Mostly intended for composite-operations such that they can apply repetition and state-dependent registries.
        :return: Array-like of decomposed operations.
        """
        result: List[ICircuitOperation] = []
        for node in self._circuit_graph.get_node_iterator():
            # Apply relation-link head (Important for nested composite-operations)
            if not node.operation.has_relation:
                node.operation.relation_link = self.relation_link
            # Extend decomposed operation list
            result.extend(node.operation.decomposed_operations())
        return result
    # endregion

    # region Class Methods
    def extend(self, other: 'CircuitCompositeOperation') -> 'CircuitCompositeOperation':
        """
        WARNING: Applies modifier inplace.
        :return: Self. Extend self with other graph branch.
        """
        leaf_nodes = self._circuit_graph.leaf_nodes
        multi_relation = MultiRelationLink(
            _reference_nodes=[node.operation for node in leaf_nodes],
            _relation_to_group=MultiRelationType.LATEST,
            _relation_type=RelationType.FOLLOWED_BY,
        )
        for node in other._circuit_graph.get_node_iterator():
            if not node.operation.has_relation:
                node.operation.relation_link = multi_relation
            self.add(operation=node.operation)
        return self

    def repeat(self, times: int) -> 'CircuitCompositeOperation':
        """
        WARNING: Applies modifier inplace.
        :return: Simple repeat.
        """
        original_self = self.copy()
        for i in range(times - 1):
            self.extend(other=original_self.copy())
        return self

    def get_sub_composite_operations(self) -> List[ICircuitCompositeOperation]:
        """:return: Array-like of all operations that are of instance ICircuitCompositeOperation."""
        result: List[ICircuitCompositeOperation] = []
        for node in self._circuit_graph.get_node_iterator():
            if isinstance(node.operation, CircuitCompositeOperation):
                result.append(node.operation)
                result.extend(node.operation.get_sub_composite_operations())
        return result
    # endregion

