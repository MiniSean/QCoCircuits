# -------------------------------------------
# Module containing functionality for optimizing gate sequence based on constraints.
# -------------------------------------------
from dataclasses import dataclass
from typing import List, Iterator, Generic, Dict, Union
import numpy as np
from math import factorial as f, ceil
from tqdm import tqdm
from qce_circuit.utilities.custom_exceptions import (
    IndexOutOfRangeException,
    ExceedingCombinationCountException,
)
from qce_circuit.connectivity.intrf_channel_identifier import IEdgeID, IQubitID
from qce_circuit.connectivity.intrf_connectivity import IConnectivityLayer
from qce_circuit.connectivity.intrf_connectivity_surface_code import (
    ISurfaceCodeLayer,
    FrequencyGroupIdentifier,
)
from qce_circuit.connectivity.intrf_connectivity_gate_sequence import (
    Operation,
    TIdentifier,
    GateSequenceLayer,
)
from qce_circuit.connectivity.connectivity_surface_code import (
    get_requires_parking,
    on_moving_side,
    get_neighbors,
)
from qce_circuit.connectivity.generic_gate_sequence import GenericSurfaceCode
from qce_circuit.utilities.array_manipulation import unique_in_order
from qce_circuit.utilities.combinatorics import generate_unique_subgroup_combinations


@dataclass(frozen=True)
class OperationConstraint(Generic[TIdentifier]):
    """Data class, containing operation constraints."""
    operation: Operation[TIdentifier]
    forbidden_operations: Dict[IQubitID, List[Operation]]

    # region Class Properties
    @property
    def constraint_operations(self) -> List[Operation]:
        """:return: Array-like of non-allowed Operations based on constraints."""
        unique_flatten_forbidden: List[Operation] = unique_in_order([operation for operations in self.forbidden_operations.values() for operation in operations])
        return unique_flatten_forbidden
    # endregion

    # region Class Methods
    def get_allowed_operations(self, connectivity: ISurfaceCodeLayer) -> List[Operation]:
        """:return: Array-like of allowed Operations based on constraints and connectivity."""
        constraint_operations: List[Operation] = self.constraint_operations
        possible_operations: List[Operation] = unique_in_order([operation for qubit_id in connectivity.qubit_ids for operation in self.get_possible_operations(qubit_id, connectivity)])
        allowed_operations: List[Operation] = [operation for operation in possible_operations if operation not in constraint_operations]
        return allowed_operations
    # endregion

    # region Static Class Methods
    @staticmethod
    def get_possible_operations(qubit_id: IQubitID, connectivity: IConnectivityLayer) -> List[Operation]:
        """:return: Array-like of possible (allowed) operations based on connectivity."""
        result: List[Operation] = []
        result.append(Operation.type_idle(qubit_id))
        result.append(Operation.type_park(qubit_id))
        for edge_id in connectivity.get_edges(qubit_id):
            result.append(Operation.type_gate(edge_id))
        return result

    @staticmethod
    def get_requires_idle(element: IQubitID, edge_ids: List[IEdgeID], connectivity: ISurfaceCodeLayer) -> bool:
        """
        Determines whether qubit-ID is required to stay idle based on participation in flux dance and frequency group.
        :return: Boolean, whether qubit-ID requires to stay idle.
        """
        spectator: bool = np.any([element in get_neighbors(edge_id, connectivity) for edge_id in edge_ids])
        # Guard clause, if qubit-ID does not spectate the flux-dance, no hard requirement for idling
        if not spectator:
            return False
        # Check if qubit-ID requires idling based on its frequency group ID and active two-qubit gates.
        frequency_group: FrequencyGroupIdentifier = connectivity.get_frequency_group_identifier(element=element)
        # Idling is required if any neighboring qubit from a lower frequency group is part of an edge.
        neighboring_qubit_ids: List[IQubitID] = connectivity.get_neighbors(qubit=element, order=1)
        involved_qubits: List[IQubitID] = [qubit_id for edge_id in edge_ids for qubit_id in edge_id.qubit_ids]
        involved_edges: List[IEdgeID] = [edge_id for edge_id in edge_ids for _ in edge_id.qubit_ids]
        involved_neighbors: List[IQubitID] = [qubit_id for qubit_id in neighboring_qubit_ids if qubit_id in involved_qubits]
        involved_neighbor_edges: List[IEdgeID] = [involved_edges[involved_qubits.index(qubit_id)] for qubit_id in neighboring_qubit_ids if qubit_id in involved_qubits]
        involved_frequency_groups: List[FrequencyGroupIdentifier] = [connectivity.get_frequency_group_identifier(element=qubit_id) for qubit_id in involved_neighbors]
        return any([
            neighbor_frequency_group.is_lower_than(frequency_group) and not on_moving_side(neighbor_qubit_id, neighbor_edge_id, connectivity)
            for neighbor_qubit_id, neighbor_frequency_group, neighbor_edge_id in zip(involved_neighbors, involved_frequency_groups, involved_neighbor_edges)
        ])

    @staticmethod
    def intersect(element: Union[IQubitID, IEdgeID], edge_id: IEdgeID) -> bool:
        """:return: True if element intersects with edge."""
        if isinstance(element, IQubitID):
            return edge_id.contains(element)
        if isinstance(element, IEdgeID):
            return np.any([edge_id.contains(qubit_id) for qubit_id in element.qubit_ids])
        return False

    @staticmethod
    def get_forbidden_operations(operation: Operation, qubit_id: IQubitID, connectivity: ISurfaceCodeLayer) -> List[Operation]:
        """:return: Array-like of forbidden operations based on parking and frequency constraints."""
        # Guard clause, if qubit is part of operation, all operations (except focus operation) are forbidden
        if operation.contains(qubit_id):
            return [_operation for _operation in OperationConstraint.get_possible_operations(qubit_id=qubit_id, connectivity=connectivity) if _operation != operation]

        # Guard clause, if qubit is outside direct neighbors, no forbidden operations
        outside_direct_neighbors: bool = qubit_id not in get_neighbors(operation.identifier, connectivity, order=1)
        if outside_direct_neighbors:
            return []

        result: List[Operation] = []
        # Determine whether qubit needs to be parked or lowered for the operation
        operating_edges: List[IEdgeID] = [] if not isinstance(operation.identifier, IEdgeID) else [operation.identifier]

        # Filter edges that are not part of operations
        available_edges: List[IEdgeID] = [edge_id for edge_id in connectivity.get_edges(qubit_id) if not OperationConstraint.intersect(operation.identifier, edge_id)]
        forbidden_to_move_down: bool = OperationConstraint.get_requires_idle(qubit_id, operating_edges, connectivity)
        forbidden_to_stay_idle: bool = get_requires_parking(qubit_id, operating_edges, connectivity)

        # Exclude edges not part of available edges
        for edge_id in connectivity.get_edges(qubit_id):
            if edge_id not in available_edges:
                result.append(Operation.type_gate(edge_id))

        if forbidden_to_stay_idle:
            result.append(Operation.type_idle(qubit_id))
            # Add gate if qubit is on the 'moving' side of the gate
            for edge_id in available_edges:
                if not on_moving_side(qubit_id, edge_id, connectivity):
                    result.append(Operation.type_gate(edge_id))

        if forbidden_to_move_down:
            result.append(Operation.type_park(qubit_id))
            # Add gate if qubit is not on the 'moving' side of the gate
            for edge_id in available_edges:
                if on_moving_side(qubit_id, edge_id, connectivity):
                    result.append(Operation.type_gate(edge_id))

        return result
    # endregion


@dataclass(frozen=True)
class OperationSequence:
    """
    Data class, containing array-like of operations.
    """
    operations: List[List[Operation]]

    # region Class Properties
    @property
    def operation_count(self) -> int:
        """:return: Total number of operations in sequence."""
        return int(np.sum([len(operations) for operations in self.operations]))

    @property
    def gate_operations(self) -> List[List[Operation[IEdgeID]]]:
        """:return: Array-like of list of gate operations."""
        result: List[List[Operation[IEdgeID]]] = []
        for sub_group in self.operations:
            result.append([operation for operation in sub_group if isinstance(operation.identifier, IEdgeID)])
        return result
    # endregion

    # region Class Methods
    def get_required_parkings(self, connectivity: ISurfaceCodeLayer) -> List[List[Operation[IQubitID]]]:
        """:return: A list of lists, each containing operations required for parking qubits based on connectivity."""
        result: List[List[Operation[IQubitID]]] = []
        for sub_group in self.gate_operations:
            edge_ids: List[IEdgeID] = [operation.identifier for operation in sub_group]
            sub_result: List[Operation[IQubitID]] = []

            for qubit_id in connectivity.qubit_ids:
                requires_parking: bool = get_requires_parking(qubit_id, edge_ids, connectivity)
                if requires_parking:
                    sub_result.append(Operation.type_park(qubit_id))
            result.append(sub_result)
        return result

    def get_parking_count(self, connectivity: ISurfaceCodeLayer) -> int:
        """:return: Total count of parking operations required based on the given connectivity."""
        return int(np.sum([len(operations) for operations in self.get_required_parkings(connectivity)]))

    def get_unique_parking_count(self, connectivity: ISurfaceCodeLayer) -> int:
        """
        :return: Count of unique parking operations required, eliminating duplicates within the operation sequence.
        """
        return len(unique_in_order([operation for operations in self.get_required_parkings(connectivity) for operation in operations]))

    def to_generic_surface_code(self, connectivity: ISurfaceCodeLayer) -> GenericSurfaceCode:
        """:return: GateSequenceLayer based on operation sequence index."""
        gate_operations: List[List[Operation[IEdgeID]]] = self.gate_operations
        park_operations: List[List[Operation[IQubitID]]] = self.get_required_parkings(
            connectivity=connectivity)

        return GenericSurfaceCode(
            gate_sequences=[
                GateSequenceLayer(
                    _gate_operations=_gate_operations,
                    _park_operations=_park_operations,
                )
                for _gate_operations, _park_operations in zip(gate_operations, park_operations)
            ],
            parity_group_z=connectivity.parity_group_z,
            parity_group_x=connectivity.parity_group_x,
        )
    # endregion


@dataclass(frozen=True)
class GateSequenceIdentifier:
    """
    Data class, containing collection of index pointers and corresponding edge-IDs.
    """
    index_pointers: List[List[List[int]]]
    edge_ids: List[IEdgeID]

    # region Class Properties
    @property
    def length(self) -> int:
        return len(self.index_pointers)
    # endregion

    # region Class Methods
    def construct_operation_sequence_at(self, index: int) -> OperationSequence:
        """:return: OperationSequence based on gate-sequence identifier and index."""
        # Guard clause, raise exception if index falls outside index pointer range
        if not 0 <= index < self.length:
            raise IndexOutOfRangeException(f"Index {index} not between 0 and {self.length}.")

        operations: List[List[Operation[IEdgeID]]] = []
        for sub_sequence_indices in self.index_pointers[index]:
            target_gates: List[IEdgeID] = [self.edge_ids[index] for index in sub_sequence_indices]
            target_operations: List[Operation[IEdgeID]] = [Operation.type_gate(edge_id) for edge_id in target_gates]
            operations.append(target_operations)
        return OperationSequence(
            operations=operations,
        )

    def construct_operation_sequences(self) -> Iterator[OperationSequence]:
        """:return: Iterator of OperationSequences."""
        for i in tqdm(range(self.length), desc="Convert combination pointers to gate-sequences"):
            yield self.construct_operation_sequence_at(index=i)

    def construct_minimal_parking_sequence(self, connectivity: ISurfaceCodeLayer) -> OperationSequence:
        """:return: Constructed OperationSequence after iterating to find minimal parking."""
        sequences: List[OperationSequence] = list(self.construct_operation_sequences())
        # Sort on minimal amount of parking
        increase_parking_count: List[OperationSequence] = sorted(sequences, key=lambda x: x.get_unique_parking_count(connectivity))
        return increase_parking_count[0]
    # endregion


@dataclass(frozen=True)
class GateSequenceGenerator:
    """
    Data class, containing array-like of edges and surface-code connectivity to generate gate sequences.
    """
    included_edge_ids: List[IEdgeID]
    connectivity: ISurfaceCodeLayer

    # region Class Properties
    @property
    def edge_index_pointers(self) -> List[int]:
        """:return: Index pointers to each of the included edge-IDs."""
        return list(range(len(self.included_edge_ids)))
    # endregion

    # region Class Methods
    def construct_allowed_gate_sequences(self, subgroup_size: int = 3, max_combinations: int = 20000) -> GateSequenceIdentifier:
        """
        :param subgroup_size: Integer group-size, describing the maximum number of gates in each sequence step.
        :param max_combinations: Implicit limit to number of combinations to calculate.
         Will through an exception if exceeded.
        :return: Constructed gate-sequence identifier based on combinatorics.
        """
        element_indices: List[int] = self.edge_index_pointers
        nr_expected_combinations: int = self.get_combination_size(nr_elements=len(element_indices), group_size=subgroup_size)
        # Guard clause, if calculated number of combinations exceeds max (allowed) combination, raise warning
        if nr_expected_combinations > max_combinations:
            raise ExceedingCombinationCountException(f"Warning number of expected combinations ({nr_expected_combinations}), exceeds limit ({max_combinations}). Either reduce number of combinations or explicitly specify 'max_combinations' argument.")

        groups: List[List[List[int]]] = generate_unique_subgroup_combinations(element_indices, subgroup_size=subgroup_size)
        index_pointers: List[List[List[int]]] = []
        for gate_sequence_indices in tqdm(groups, desc="Processing all gate-sequence combinations"):

            gate_sequence_accepted: bool = True
            for sub_sequence_indices in gate_sequence_indices:

                target_gates: List[IEdgeID] = [self.included_edge_ids[index] for index in sub_sequence_indices]
                target_operations: List[Operation] = [Operation.type_gate(edge_id) for edge_id in target_gates]
                mutually_allowed: bool = self.get_mutually_allowed(target_operations, self.connectivity)
                if not mutually_allowed:
                    gate_sequence_accepted = False
                    break

            if gate_sequence_accepted:
                index_pointers.append(gate_sequence_indices)

        return GateSequenceIdentifier(
            index_pointers=index_pointers,
            edge_ids=self.included_edge_ids,
        )
    # endregion

    # region Static Class Methods
    @staticmethod
    def get_combination_size(nr_elements: int, group_size: int) -> int:
        """:return: Calculation of number of expected combinations, or 0 if not possible."""
        if group_size > nr_elements or nr_elements % group_size != 0:
            return 0  # No valid combinations possible

        nr_groups: int = ceil(nr_elements / group_size)
        return ceil(f(nr_elements) / (f(group_size)**nr_groups * f(nr_groups)))

    @staticmethod
    def construct_operation_constraints(operation: Operation, connectivity: ISurfaceCodeLayer) -> OperationConstraint:
        return OperationConstraint(
            operation=operation,
            forbidden_operations={
                qubit_id: OperationConstraint.get_forbidden_operations(operation, qubit_id, connectivity)
                for qubit_id in connectivity.qubit_ids
            }
        )

    @staticmethod
    def get_mutually_allowed(operations: List[Operation], connectivity: ISurfaceCodeLayer) -> bool:
        for target_operation in operations:
            # Construct constraints
            operation_constraint: OperationConstraint = GateSequenceGenerator.construct_operation_constraints(target_operation, connectivity)
            allowed_operations: List[Operation] = operation_constraint.get_allowed_operations(connectivity)
            # Check if all (other) operations satisfy these constraints
            for simultaneous_operation in operations:
                if simultaneous_operation not in allowed_operations:
                    return False
        return True
    # endregion
