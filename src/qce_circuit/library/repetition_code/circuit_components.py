# -------------------------------------------
# Module containing circuit components for constructing full repetition-code circuit.
# -------------------------------------------
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
import numpy as np
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException
from qce_circuit import (
    DeclarativeCircuit,
    AcquisitionRegistry,
    RegistryAcquisitionStrategy,
    FixedDurationStrategy,
    FixedRepetitionStrategy,
)
from qce_circuit.language import InitialStateContainer
from qce_circuit.addon_stim.circuit_operations import DetectorOperation, CoordinateShiftOperation
from qce_circuit.connectivity import (
    GateSequenceLayer,
    Operation,
    IQubitID,
    QubitIDObj,
    IEdgeID,
    EdgeIDObj,
)
from qce_circuit.connectivity.generic_gate_sequence import (
    IGenericSurfaceCodeLayer,
    GenericSurfaceCode,
)
from qce_circuit.connectivity.connectivity_surface_code import get_requires_parking
from qce_circuit.utilities.array_manipulation import unique_in_order
from qce_circuit.structure.circuit_operations import (
    Reset,
    Rx180,
    Ry90,
    Rym90,
    CPhase,
    Barrier,
    Wait,
    DispersiveMeasure,
)
from qce_circuit.structure.intrf_circuit_operation import (
    RelationLink,
    RelationType,
)
from qce_circuit.structure.intrf_acquisition_operation import IAcquisitionOperation
from qce_circuit.structure.intrf_circuit_operation import ICircuitOperation
from qce_circuit.library.repetition_code.repetition_code_connectivity import Repetition9Code


class IRepetitionCodeDescription(ABC):
    """
    Interface class, describing methods and properties for repetition-code circuit construction.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def qubit_ids(self) -> List[IQubitID]:
        """:return: (All) qubit-ID's in connectivity."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def data_qubit_ids(self) -> List[IQubitID]:
        """:return: (All) Data-qubit-ID's in connectivity."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def ancilla_qubit_ids(self) -> List[IQubitID]:
        """:return: (All) Ancilla-qubit-ID's in connectivity."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def gate_sequences(self) -> List[GateSequenceLayer]:
        """:return: Array-like of gate sequences."""
        raise InterfaceMethodException

    @property
    def qubit_indices(self) -> List[int]:
        """:return: (All) qubit-indices."""
        return [self.map_qubit_id_to_circuit_index(qubit_id) for qubit_id in self.qubit_ids]

    @property
    def data_qubit_indices(self) -> List[int]:
        """:return: (All) Data-qubit-indices."""
        return [self.map_qubit_id_to_circuit_index(qubit_id) for qubit_id in self.data_qubit_ids]

    @property
    def ancilla_qubit_indices(self) -> List[int]:
        """:return: (All) Ancilla-qubit-indices."""
        return [self.map_qubit_id_to_circuit_index(qubit_id) for qubit_id in self.ancilla_qubit_ids]

    @property
    def gate_sequence_count(self) -> int:
        """:return: Number of gate sequence layers."""
        return len(self.gate_sequences)

    @property
    def circuit_channel_map(self) -> Dict[int, IQubitID]:
        """:return: Dictionary that maps circuit channel index to identifier."""
        return {
            self.map_qubit_id_to_circuit_index(qubit_id): qubit_id
            for qubit_id in self.qubit_ids
        }
    # endregion

    # region Interface Methods
    @abstractmethod
    def map_qubit_id_to_circuit_index(self, qubit_id: IQubitID) -> int:
        """
        :param qubit_id: Identifier that is mapped to circuit channel index.
        :return: Circuit channel index corresponding to qubit-ID.
        """
        raise InterfaceMethodException

    @abstractmethod
    def get_operations(self, initial_state: InitialStateContainer, **kwargs) -> List[ICircuitOperation]:
        """
        :param initial_state: Container with qubit-index to initial state enum mapping.
        :return: Array-like of circuit operations, corresponding to initial state preparation.
        """
        raise InterfaceMethodException

    def get_element(self, index: int) -> IQubitID:
        """:return: Qubit-ID element corresponding to index."""
        return self.qubit_ids[index]

    def get_index(self, element: IQubitID) -> int:
        """:return: Index corresponding to Qubit-ID element."""
        return self.qubit_ids.index(element)

    def get_edges(self, qubit: IQubitID) -> List[IEdgeID]:
        """:return: All qubit-to-qubit edges from qubit-ID."""
        result: List[IEdgeID] = []
        edge_ids: List[IEdgeID] = unique_in_order([identifier for sequence in self.gate_sequences for identifier in sequence.edge_ids])
        for edge in edge_ids:
            if edge.contains(element=qubit):
                result.append(edge)
        return result

    def get_gate_sequence_indices(self, sequence_index: int) -> Optional[List[Tuple[int, int]]]:
        """
        :param sequence_index: Gate sequence index. If index is out of range, return None.
        :return: (Optional) Array-like of two-integer Tuples.
        """
        # Guard clause, if index is out of range, return None.
        if not 0 <= sequence_index < len(self.gate_sequences):
            return None

        sequence: GateSequenceLayer = self.gate_sequences[sequence_index]
        result: List[Tuple[int, int]] = []
        for edge in sequence.edge_ids:
            result.append((
                self.map_qubit_id_to_circuit_index(edge.qubit_ids[0]),
                self.map_qubit_id_to_circuit_index(edge.qubit_ids[1])
            ))
        return result

    def get_active_ancilla_indices(self, sequence_index: int) -> Optional[List[int]]:
        """
        Determines which ancilla indices need to be 'active' for a given sequence index.
        :param sequence_index: Gate sequence index. If index is out of range, return None.
        :return: (Optional) Array-like of single-integer (corresponding to ancilla-index).
        """
        # Guard clause, if index is out of range, return None.
        if not 0 <= sequence_index < len(self.gate_sequences):
            return None

        ancilla_ids: List[IQubitID] = self.ancilla_qubit_ids
        sequence: GateSequenceLayer = self.gate_sequences[sequence_index]
        result: List[int] = []
        for edge in sequence.edge_ids:
            for qubit_id in edge.qubit_ids:
                if qubit_id in ancilla_ids:
                    result.append(self.map_qubit_id_to_circuit_index(qubit_id))
        return result

    def to_sequence(self) -> IGenericSurfaceCodeLayer:
        """:return: Trivial conversion from circuit description to gate sequence (layout)."""

        return GenericSurfaceCode(
            gate_sequences=self.gate_sequences,
            parity_group_x=Repetition9Code().parity_group_x,
            parity_group_z=Repetition9Code().parity_group_z,
        )
    # endregion


@dataclass(frozen=True)
class RepetitionCodeDescription(IRepetitionCodeDescription):
    """
    Data class, describing (dynamic) 1D qubit chain connectivity.
    """
    _data_qubit_ids: List[IQubitID]
    _ancilla_qubit_ids: List[IQubitID]
    _gate_sequences: List[GateSequenceLayer]
    _qubit_index_map: Dict[IQubitID, int]
    """Mapping from Qubit-ID to circuit channel index."""

    # region Interface Properties
    @property
    def qubit_ids(self) -> List[IQubitID]:
        """:return: (All) qubit-ID's in connectivity."""
        # Example arrays
        a = np.asarray(self.data_qubit_ids)
        b = np.asarray(self.ancilla_qubit_ids)

        # Ensure a and b are of the same length or handle cases where they are not
        length = min(len(a), len(b))
        result = np.empty((length * 2,), dtype=a.dtype)

        # Fill in c by alternating elements from a and b
        result[0::2], result[1::2] = a[:length], b[:length]

        # If a and b were of different lengths, append the remaining elements
        if len(a) > length:
            result = np.append(result, a[length:])
        elif len(b) > length:
            result = np.append(result, b[length:])
        return list(result)

    @property
    def data_qubit_ids(self) -> List[IQubitID]:
        """:return: (All) Data-qubit-ID's in connectivity."""
        return self._data_qubit_ids

    @property
    def ancilla_qubit_ids(self) -> List[IQubitID]:
        """:return: (All) Ancilla-qubit-ID's in connectivity."""
        return self._ancilla_qubit_ids

    @property
    def gate_sequences(self) -> List[GateSequenceLayer]:
        """:return: Array-like of gate sequences."""
        return self._gate_sequences
    # endregion

    # region Interface Methods
    def map_qubit_id_to_circuit_index(self, qubit_id: IQubitID) -> int:
        """
        :param qubit_id: Identifier that is mapped to circuit channel index.
        :return: Circuit channel index corresponding to qubit-ID.
        """
        return self._qubit_index_map[qubit_id]

    def get_operations(self, initial_state: InitialStateContainer, **kwargs) -> List[ICircuitOperation]:
        """
        :param initial_state: Container with qubit-index to initial state enum mapping.
        :return: Array-like of circuit operations, corresponding to initial state preparation.
        """
        return [
            initial_state.get_operation(
                qubit_index=self.map_qubit_id_to_circuit_index(
                    qubit_id=self.data_qubit_ids[initial_state_index],
                ),
                initial_state_index=initial_state_index,
                **kwargs,
            )
            for initial_state_index in initial_state.initial_states.keys()
        ]
    # endregion

    # region Class Methods
    @classmethod
    def from_chain(cls, length: int) -> 'RepetitionCodeDescription':
        """:return: Class method constructor based on chain length."""
        qubit_ids: List[IQubitID] = [QubitIDObj(f'D{i}') for i in range(length)]
        data_qubit_ids: List[IQubitID] = qubit_ids[::2]
        ancilla_qubit_ids: List[IQubitID] = qubit_ids[1::2]
        edge_ids: List[IEdgeID] = [EdgeIDObj(qubit_id0, qubit_id1) for qubit_id0, qubit_id1 in zip(qubit_ids, qubit_ids[1:])]
        gate_sequences: List[GateSequenceLayer] = [
            GateSequenceLayer(
                _park_operations=[],
                _gate_operations=[Operation.type_gate(edge_id=edge) for edge in _edges]
            )
            for _edges in [edge_ids[i::2] for i in range(2)] if len(_edges) > 0
        ]
        qubit_index_map: Dict[IQubitID, int] = {qubit_id: i for i, qubit_id in enumerate(qubit_ids)}
        return RepetitionCodeDescription(
            _data_qubit_ids=data_qubit_ids,
            _ancilla_qubit_ids=ancilla_qubit_ids,
            _gate_sequences=gate_sequences,
            _qubit_index_map=qubit_index_map,
        )

    @classmethod
    def from_initial_state(cls, initial_state: InitialStateContainer) -> 'RepetitionCodeDescription':
        """:return: Class method constructor based on initial data-qubit state."""
        code_distance: int = initial_state.distance
        chain_distance: int = 2 * code_distance - 1
        return RepetitionCodeDescription.from_chain(length=chain_distance)

    @classmethod
    def from_connectivity(cls, involved_qubit_ids: List[IQubitID], connectivity: IGenericSurfaceCodeLayer) -> 'RepetitionCodeDescription':
        """:return: Class method constructor based on pre-defined connectivity and involved qubit-ID's."""
        data_qubit_ids: List[IQubitID] = [qubit_id for qubit_id in involved_qubit_ids if qubit_id in connectivity.data_qubit_ids]
        ancilla_qubit_ids: List[IQubitID] = [qubit_id for qubit_id in involved_qubit_ids if qubit_id in connectivity.ancilla_qubit_ids]
        # Populate gate sequence part of involved qubit-ID's
        gate_sequences: List[GateSequenceLayer] = []
        for i in range(connectivity.gate_sequence_count):
            entire_gate_sequence: GateSequenceLayer = connectivity.get_gate_sequence_at_index(index=i)
            # Mandatory gate operations
            gate_operations: List[Operation[IEdgeID]] = [element for element in entire_gate_sequence.gate_operations if all([qubit_id in involved_qubit_ids for qubit_id in element.identifier.qubit_ids])]
            # Dynamic park operations
            edge_identifiers: List[IEdgeID] = [element.identifier for element in gate_operations]
            park_operations: List[Operation[IQubitID]] = [Operation.type_park(element) for element in connectivity.qubit_ids if get_requires_parking(element=element, edge_ids=edge_identifiers, connectivity=connectivity)]
            # Only include park- and gate-operations for which all identifiers are part of involved qubit-ID's
            subset_gate_sequence: GateSequenceLayer = GateSequenceLayer(
                _park_operations=park_operations,
                _gate_operations=gate_operations,
            )
            non_empty_sequence: bool = len(subset_gate_sequence.park_operations) > 0 or len(subset_gate_sequence.gate_operations) > 0
            if non_empty_sequence:
                gate_sequences.append(subset_gate_sequence)
        # Setup default qubit index map
        qubit_index_map: Dict[IQubitID, int] = {qubit_id: i for i, qubit_id in enumerate(involved_qubit_ids)}
        # Return constructed connectivity
        return RepetitionCodeDescription(
            _data_qubit_ids=data_qubit_ids,
            _ancilla_qubit_ids=ancilla_qubit_ids,
            _gate_sequences=gate_sequences,
            _qubit_index_map=qubit_index_map,
        )
    # endregion


def get_last_acquisition_operation(_circuit: DeclarativeCircuit, qubit_index: Optional[int] = None) -> Optional[IAcquisitionOperation]:
    """:return: (Optional) last DispersiveMeasure for specific qubit index, added to the circuit."""
    added_operations: List[ICircuitOperation] = _circuit.operations
    for i in range(len(added_operations)):
        operation: ICircuitOperation = added_operations[-1 - i]
        operation_acceptance: bool = isinstance(operation, IAcquisitionOperation)
        if operation_acceptance:
            qubit_index_acceptance: bool = qubit_index is None or operation.qubit_index == qubit_index
            if qubit_index_acceptance:
                return operation
    return None


def get_repetition_code_connectivity(initial_state: InitialStateContainer) -> RepetitionCodeDescription:
    return RepetitionCodeDescription.from_initial_state(initial_state=initial_state)


def get_circuit_initialize(connectivity: IRepetitionCodeDescription, initial_state: InitialStateContainer) -> DeclarativeCircuit:
    result: DeclarativeCircuit = DeclarativeCircuit()
    qubit_indices: List[int] = connectivity.qubit_indices
    result.add(Barrier(qubit_indices))
    for operation in connectivity.get_operations(initial_state=initial_state):
        result.add(operation)
    result.add(Barrier(qubit_indices))
    return result

def get_circuit_initialize_simplified(connectivity: IRepetitionCodeDescription, initial_state: InitialStateContainer) -> DeclarativeCircuit:
    result: DeclarativeCircuit = DeclarativeCircuit()
    for operation in connectivity.get_operations(initial_state=initial_state):
        result.add(operation)
    return result


def get_circuit_initialize_with_heralded(connectivity: IRepetitionCodeDescription, initial_state: InitialStateContainer, registry: AcquisitionRegistry) -> DeclarativeCircuit:
    result: DeclarativeCircuit = DeclarativeCircuit()
    qubit_indices: List[int] = connectivity.qubit_indices
    for qubit_index in qubit_indices:
        result.add(Reset(qubit_index))
    for qubit_index in qubit_indices:
        result.add(DispersiveMeasure(
            qubit_index,
            acquisition_strategy=RegistryAcquisitionStrategy(registry),
            acquisition_tag='heralded',
        ))
    result.add(get_circuit_initialize(
        connectivity=connectivity,
        initial_state=initial_state,
    ))
    return result


def get_circuit_final_measurement(connectivity: IRepetitionCodeDescription, registry: AcquisitionRegistry) -> DeclarativeCircuit:
    result: DeclarativeCircuit = DeclarativeCircuit()
    for data_index in connectivity.data_qubit_indices:
        result.add(DispersiveMeasure(
            data_index,
            acquisition_strategy=RegistryAcquisitionStrategy(registry),
            acquisition_tag='final',
        ))
    return result


def get_circuit_qec_round(connectivity: IRepetitionCodeDescription, registry: AcquisitionRegistry) -> DeclarativeCircuit:
    result: DeclarativeCircuit = DeclarativeCircuit()

    ancilla_indices: List[int] = connectivity.ancilla_qubit_indices
    all_indices: List[int] = connectivity.qubit_indices
    current_active_ancilla_indices: List[int] = []

    for sequence_index in range(connectivity.gate_sequence_count):
        # Check if ancilla's need to be 'activated'
        sequence_active_ancilla_indices: List[int] = connectivity.get_active_ancilla_indices(sequence_index)
        next_sequence_active_ancilla_indices: Optional[List[int]] = connectivity.get_active_ancilla_indices(sequence_index + 1)
        sequence_active_gate_indices: List[Tuple[int, int]] = connectivity.get_gate_sequence_indices(sequence_index)

        require_activation: List[int] = [qubit_index for qubit_index in sequence_active_ancilla_indices if qubit_index not in current_active_ancilla_indices]
        require_closure: List[int] = sequence_active_ancilla_indices
        if next_sequence_active_ancilla_indices is not None:
            require_closure = [qubit_index for qubit_index in sequence_active_ancilla_indices if qubit_index not in next_sequence_active_ancilla_indices]
        # Update current active ancilla indices
        current_active_ancilla_indices = sequence_active_ancilla_indices

        # Schedule Ancilla basis rotation for 'activation'
        for qubit_index in require_activation:
            result.add(Rym90(qubit_index))
        if len(require_activation) > 0:
            result.add(Barrier(all_indices))
        # Schedule two-qubit gate
        for index0, index1 in sequence_active_gate_indices:
            result.add(CPhase(index0, index1))
        if len(sequence_active_gate_indices) > 0:
            result.add(Barrier(all_indices))
        # Schedule Ancilla basis rotation for 'closure'
        for qubit_index in require_closure:
            result.add(Ry90(qubit_index))

    # Ancilla measurement
    result.add(Barrier(all_indices))
    for ancilla_index in ancilla_indices:
        result.add(DispersiveMeasure(
            ancilla_index,
            acquisition_strategy=RegistryAcquisitionStrategy(registry),
            acquisition_tag='parity',
        ))
    return result


def get_circuit_qec_round_with_dynamical_decoupling(connectivity: IRepetitionCodeDescription, registry: AcquisitionRegistry) -> DeclarativeCircuit:
    result: DeclarativeCircuit = DeclarativeCircuit()

    data_indices: List[int] = connectivity.data_qubit_indices
    ancilla_indices: List[int] = connectivity.ancilla_qubit_indices
    all_indices: List[int] = connectivity.qubit_indices
    current_active_ancilla_indices: List[int] = []

    for sequence_index in range(connectivity.gate_sequence_count):
        # Check if ancilla's need to be 'activated'
        sequence_active_ancilla_indices: List[int] = connectivity.get_active_ancilla_indices(sequence_index)
        next_sequence_active_ancilla_indices: Optional[List[int]] = connectivity.get_active_ancilla_indices(sequence_index + 1)
        sequence_active_gate_indices: List[Tuple[int, int]] = connectivity.get_gate_sequence_indices(sequence_index)

        require_activation: List[int] = [qubit_index for qubit_index in sequence_active_ancilla_indices if qubit_index not in current_active_ancilla_indices]
        require_closure: List[int] = sequence_active_ancilla_indices
        if next_sequence_active_ancilla_indices is not None:
            require_closure = [qubit_index for qubit_index in sequence_active_ancilla_indices if qubit_index not in next_sequence_active_ancilla_indices]
        # Update current active ancilla indices
        current_active_ancilla_indices = sequence_active_ancilla_indices

        # Schedule Ancilla basis rotation for 'activation'
        for qubit_index in require_activation:
            result.add(Rym90(qubit_index))
        if len(require_activation) > 0:
            result.add(Barrier(all_indices))
        # Schedule two-qubit gate
        for index0, index1 in sequence_active_gate_indices:
            result.add(CPhase(index0, index1))
        if len(sequence_active_gate_indices) > 0:
            result.add(Barrier(all_indices))
        # Schedule Ancilla basis rotation for 'closure'
        for qubit_index in require_closure:
            result.add(Ry90(qubit_index))

    # Ancilla measurement
    result.add(Barrier(all_indices))
    for ancilla_index in ancilla_indices:
        result.add(DispersiveMeasure(
            ancilla_index,
            acquisition_strategy=RegistryAcquisitionStrategy(registry),
            acquisition_tag='parity',
        ))
    dynamical_decoupling_wait = FixedDurationStrategy(duration=0.5)
    for data_index in data_indices:
        result.add(Wait(data_index, duration_strategy=dynamical_decoupling_wait))
        result.add(Rx180(data_index))
        result.add(Wait(data_index, duration_strategy=dynamical_decoupling_wait))
    return result


def get_circuit_qec_round_with_dynamical_decoupling_simplified(connectivity: IRepetitionCodeDescription, registry: AcquisitionRegistry) -> DeclarativeCircuit:
    """
    :return: DeclarativeCircuit containing (repetition-code) QEC-cycle with dynamical decoupling.
    Prioritizes (simplified) readability over operation accuracy. (Neglecting exact circuit implementation)
    """
    result: DeclarativeCircuit = DeclarativeCircuit()

    data_indices: List[int] = connectivity.data_qubit_indices
    ancilla_indices: List[int] = connectivity.ancilla_qubit_indices
    all_indices: List[int] = connectivity.qubit_indices
    current_active_ancilla_indices: List[int] = []

    relation_activation = RelationLink.no_relation()
    for sequence_index in range(connectivity.gate_sequence_count):
        # Check if ancilla's need to be 'activated'
        sequence_active_ancilla_indices: List[int] = connectivity.get_active_ancilla_indices(sequence_index)
        next_sequence_active_ancilla_indices: Optional[List[int]] = connectivity.get_active_ancilla_indices(sequence_index + 1)
        sequence_active_gate_indices: List[Tuple[int, int]] = connectivity.get_gate_sequence_indices(sequence_index)

        require_activation: List[int] = [qubit_index for qubit_index in sequence_active_ancilla_indices if qubit_index not in current_active_ancilla_indices]
        require_closure: List[int] = sequence_active_ancilla_indices
        if next_sequence_active_ancilla_indices is not None:
            require_closure = [qubit_index for qubit_index in sequence_active_ancilla_indices if qubit_index not in next_sequence_active_ancilla_indices]
        # Update current active ancilla indices
        current_active_ancilla_indices = sequence_active_ancilla_indices

        # Schedule Ancilla basis rotation for 'activation'
        for qubit_index in require_activation:
            result.add(Rym90(qubit_index, relation=relation_activation))
        # Schedule two-qubit gate
        for index0, index1 in sequence_active_gate_indices:
            relation = RelationLink(result.get_last_entry(), RelationType.FOLLOWED_BY)
            result.add(CPhase(index0, index1, relation=relation))
        # Schedule Ancilla basis rotation for 'closure'
        relation_activation = RelationLink(result.get_last_entry(), RelationType.FOLLOWED_BY)
        for qubit_index in require_closure:
            result.add(Ry90(qubit_index, relation=relation_activation))

    # Ancilla measurement
    # result.add(Barrier(all_indices))
    relation = RelationLink(result.get_last_entry(), RelationType.FOLLOWED_BY)
    for ancilla_index in ancilla_indices:
        result.add(DispersiveMeasure(
            ancilla_index,
            acquisition_strategy=RegistryAcquisitionStrategy(registry),
            acquisition_tag='parity',
            relation=relation,
        ))
    dynamical_decoupling_wait = FixedDurationStrategy(duration=0.5)
    for data_index in data_indices:
        result.add(Wait(data_index, duration_strategy=dynamical_decoupling_wait, relation=relation))
        result.add(Rx180(data_index))
        result.add(Wait(data_index, duration_strategy=dynamical_decoupling_wait))
    return result


def get_circuit_qec_with_detectors(connectivity: IRepetitionCodeDescription, qec_cycles: int, registry: AcquisitionRegistry) -> DeclarativeCircuit:
    result: DeclarativeCircuit = DeclarativeCircuit()
    # Guard clause, if qec-cycles is 0, return empty circuit
    if qec_cycles == 0:
        return result

    all_indices: List[int] = connectivity.qubit_indices
    ancilla_indices: List[int] = connectivity.ancilla_qubit_indices
    requires_first_sub_circuit: bool = qec_cycles > 1
    requires_third_sub_circuit_offset: bool = qec_cycles > 2
    requires_second_sub_circuit: bool = qec_cycles > 3
    no_refocusing_round: int = 1

    # ----
    if requires_first_sub_circuit:
        first_sub_circuit: DeclarativeCircuit = DeclarativeCircuit(
            repetition_strategy=FixedRepetitionStrategy(repetitions=min(2, qec_cycles - no_refocusing_round))
        )
        first_sub_circuit.add(get_circuit_qec_round_with_dynamical_decoupling(
            connectivity=connectivity,
            registry=registry,
        ))
        # Add detector operations
        for ancilla in ancilla_indices:
            first_sub_circuit.add(DetectorOperation(
                qubit_index=ancilla,
                last_acquisition_index=get_last_acquisition_operation(first_sub_circuit).circuit_level_acquisition_index,
                main_target=get_last_acquisition_operation(first_sub_circuit, qubit_index=ancilla).circuit_level_acquisition_index,
            ))
        # Add coordinate shift
        first_sub_circuit.add(CoordinateShiftOperation(qubit_indices=all_indices, space_shift=0, time_shift=1))
        result.add(first_sub_circuit)

    # ----
    if requires_second_sub_circuit:
        second_sub_circuit: DeclarativeCircuit = DeclarativeCircuit(
            repetition_strategy=FixedRepetitionStrategy(repetitions=qec_cycles - 2 - no_refocusing_round)
        )
        # QEC round with decoupling
        second_sub_circuit.add(get_circuit_qec_round_with_dynamical_decoupling(
            connectivity=connectivity,
            registry=registry,
        ))
        # Add detector operations
        for ancilla in ancilla_indices:
            second_sub_circuit.add(DetectorOperation(
                qubit_index=ancilla,
                last_acquisition_index=get_last_acquisition_operation(second_sub_circuit).circuit_level_acquisition_index,
                main_target=get_last_acquisition_operation(second_sub_circuit, qubit_index=ancilla).circuit_level_acquisition_index,
                reference_offset=2 * len(ancilla_indices),  # d_i = m_i * m_i-2, See notes
            ))
        # Add coordinate shift
        second_sub_circuit.add(CoordinateShiftOperation(qubit_indices=all_indices, space_shift=0, time_shift=1))
        result.add(second_sub_circuit)

    # ----
    third_sub_circuit: DeclarativeCircuit = DeclarativeCircuit(
        repetition_strategy=FixedRepetitionStrategy(repetitions=no_refocusing_round)
    )
    # QEC round with decoupling
    third_sub_circuit.add(get_circuit_qec_round(
        connectivity=connectivity,
        registry=registry,
    ))
    # Add detector operations
    for ancilla in ancilla_indices:
        third_sub_circuit.add(DetectorOperation(
            qubit_index=ancilla,
            last_acquisition_index=get_last_acquisition_operation(third_sub_circuit).circuit_level_acquisition_index,
            main_target=get_last_acquisition_operation(third_sub_circuit, qubit_index=ancilla).circuit_level_acquisition_index,
            reference_offset=2 * len(ancilla_indices) if requires_third_sub_circuit_offset else None,
            # d_i = m_i * m_i-2, See notes
        ))
    # Add coordinate shift
    third_sub_circuit.add(CoordinateShiftOperation(qubit_indices=all_indices, space_shift=0, time_shift=1))
    result.add(third_sub_circuit)

    return result
