# -------------------------------------------
# Module containing arbitrary length repetition-code circuit.
# -------------------------------------------
from dataclasses import dataclass
from typing import List, Union, Dict, Tuple, Optional
import numpy as np
from qce_circuit.utilities.custom_exceptions import ElementNotIncludedException
from qce_circuit.connectivity import (
    IConnectivityLayer,
    IGateSequenceLayer,
    GateSequenceLayer,
    IQubitID,
    IEdgeID,
    QubitIDObj,
    EdgeIDObj,
)
from qce_circuit.connectivity.intrf_connectivity_gate_sequence import (
    Operation,
)
from qce_circuit.structure.circuit_operations import (
    Reset,
    Identity,
    Rx180,
    Ry90,
    Rym90,
    Rx90,
    Rxm90,
    CPhase,
    Barrier,
    Wait,
    DispersiveMeasure,
)
from qce_circuit.structure.registry_acquisition import (
    RegistryAcquisitionStrategy,
    AcquisitionRegistry,
)
from qce_circuit.structure.registry_repetition import FixedRepetitionStrategy
from qce_circuit.structure.registry_duration import FixedDurationStrategy
from qce_circuit.structure.intrf_circuit_operation import ICircuitOperation
from qce_circuit.structure.intrf_acquisition_operation import IAcquisitionOperation
from qce_circuit.language import (
    DeclarativeCircuit,
    InitialStateEnum,
)

from qce_circuit.addon_stim.circuit_operations import (
    DetectorOperation,
    LogicalObservableOperation,
    CoordinateShiftOperation,
)


@dataclass(frozen=True)
class Connectivity1D(IConnectivityLayer, IGateSequenceLayer):
    """
    Data class, describing (dynamic) 1D qubit chain connectivity.
    """
    _qubit_ids: List[IQubitID]

    # region Interface Properties
    @property
    def qubit_ids(self) -> List[IQubitID]:
        """:return: (All) qubit-ID's in device layer."""
        return self._qubit_ids

    @property
    def edge_ids(self) -> List[IEdgeID]:
        """:return: (All) edge-ID's in device layer."""
        return [EdgeIDObj(qubit_id0, qubit_id1) for qubit_id0, qubit_id1 in zip(self.qubit_ids, self.qubit_ids[1:])]

    @property
    def flux_dances(self) -> List[GateSequenceLayer]:
        """:return: Array-like of flux dances."""
        edges: List[IEdgeID] = self.edge_ids
        return [
            GateSequenceLayer(
                _park_operations=[],
                _gate_operations=[Operation.type_gate(edge_id=edge) for edge in _edges]
            )
            for _edges in [edges[i::4] for i in range(4)] if len(_edges) > 0
        ]

    @property
    def gate_sequence_count(self) -> int:
        """:return: Number of gate-sequences in layer."""
        return len(self.flux_dances)
    # endregion

    # region Class Properties
    @property
    def data_qubit_ids(self) -> List[IQubitID]:
        """:return: Data-qubit IDs."""
        return self.qubit_ids[::2]

    @property
    def ancilla_qubit_ids(self) -> List[IQubitID]:
        """:return: Ancilla-qubit IDs."""
        return self.qubit_ids[1::2]

    @property
    def qubit_indices(self) -> List[int]:
        return [i for i, qubit_id in enumerate(self.qubit_ids)]

    @property
    def data_qubit_indices(self) -> List[int]:
        data_qubit_ids: List[IQubitID] = self.data_qubit_ids
        return [i for i, qubit_id in enumerate(self.qubit_ids) if qubit_id in data_qubit_ids]

    @property
    def ancilla_qubit_indices(self) -> List[int]:
        ancilla_qubit_ids: List[IQubitID] = self.ancilla_qubit_ids
        return [i for i, qubit_id in enumerate(self.qubit_ids) if qubit_id in ancilla_qubit_ids]

    @property
    def flux_dance_indices(self) -> List[List[Tuple[int, int]]]:
        result = []
        for flux_dance_index in range(self.gate_sequence_count):
            group = []
            for edge_id in self.get_gate_sequence_at_index(flux_dance_index).edge_ids:
                pair: Tuple[int, int] = (self.get_index(edge_id.qubit_ids[0]), self.get_index(edge_id.qubit_ids[1]))
                group.append(pair)
            result.append(group)
        return result

    @property
    def flux_dance_ancilla_indices(self) -> List[List[int]]:
        result = []
        group_a = []
        group_b = []

        for flux_dance_index in [0, 1]:
            for qubit_id in self.get_gate_sequence_at_index(flux_dance_index).qubit_ids:
                if qubit_id in self.ancilla_qubit_ids:
                    group_a.append(self.get_index(qubit_id))
        for flux_dance_index in [2, 3]:
            for qubit_id in self.get_gate_sequence_at_index(flux_dance_index).qubit_ids:
                if qubit_id in self.ancilla_qubit_ids:
                    group_b.append(self.get_index(qubit_id))

        result.append(list(set(group_a)))
        result.append(list(set(group_b)))
        return result
    # endregion

    # region Interface Methods
    def get_neighbors(self, qubit: IQubitID, order: int = 1) -> List[IQubitID]:
        """
        Requires :param order: to be higher or equal to 1.
        :return: qubit neighbors separated by order. (order=1, nearest neighbors).
        """
        if order > 1:
            raise NotImplementedError("Apologies, so far there has not been a use for. But feel free to implement.")
        edges: List[IEdgeID] = self.get_edges(qubit=qubit)
        result: List[IQubitID] = []
        for edge in edges:
            result.append(edge.get_connected_qubit_id(element=qubit))
        return result

    def get_edges(self, qubit: IQubitID) -> List[IEdgeID]:
        """:return: All qubit-to-qubit edges from qubit-ID."""
        result: List[IEdgeID] = []
        for edge in self.edge_ids:
            if edge.contains(element=qubit):
                result.append(edge)
        return result

    def contains(self, element: Union[IQubitID, IEdgeID]) -> bool:
        """:return: Boolean, whether element is part of connectivity layer or not."""
        if element in self.qubit_ids:
            return True
        if element in self.edge_ids:
            return True
        return False

    def get_gate_sequence_at_index(self, index: int) -> GateSequenceLayer:
        """:return: Gate-sequence object based on round index."""
        flux_dances: List[GateSequenceLayer] = self.flux_dances
        try:
            flux_dance_layer: GateSequenceLayer = flux_dances[index]
            return flux_dance_layer
        except:
            raise ElementNotIncludedException(f"Index: {index} is out of bounds for flux dance of length: {len(flux_dances)}.")

    def get_gate_sequence_from_element(self, element: IEdgeID) -> GateSequenceLayer:
        """:return: Gate-sequence layer of which edge element is part of."""
        flux_dances: List[GateSequenceLayer] = self.flux_dances
        # Assumes element is part of only a single flux-dance layer
        for flux_dance_layer in flux_dances:
            if flux_dance_layer.contains(element=element):
                return flux_dance_layer
        raise ElementNotIncludedException(f"Element: {element} is not included in any flux-dance layer.")
    # endregion

    # region Class Methods
    def get_element(self, index: int) -> IQubitID:
        return self.qubit_ids[index]

    def get_data_element(self, index: int) -> IQubitID:
        return self.data_qubit_ids[index]

    def get_index(self, element: IQubitID) -> int:
        return self.qubit_ids.index(element)

    def get_data_index(self, element: IQubitID) -> int:
        return self.data_qubit_ids.index(element)

    @classmethod
    def from_chain(cls, length: int) -> 'Connectivity1D':
        """:return: Class method constructor based on chain length."""
        return Connectivity1D(
            _qubit_ids=[QubitIDObj(f'D{i}') for i in range(length)]
        )
    # endregion


@dataclass(frozen=True)
class InitialStateContainer:
    """
    Data class, holding reference to qubits and their initial state.
    """
    initial_states: Dict[int, InitialStateEnum]
    """Index pointers to data qubits only."""

    # region Class Properties
    @property
    def distance(self) -> int:
        return len(self.initial_states)

    @property
    def as_array(self) -> np.ndarray:
        sorted_indices: List[int] = list(sorted(self.initial_states.keys()))
        # Maps initial state to binary
        to_bit_conversion: Dict[InitialStateEnum, int] = {
            InitialStateEnum.ZERO: 0,
            InitialStateEnum.MINUS: 0,
            InitialStateEnum.MINUS_I: 0,
            InitialStateEnum.ONE: 1,
            InitialStateEnum.PLUS: 1,
            InitialStateEnum.PLUS_I: 1,
        }
        return np.asarray([to_bit_conversion[self.initial_states[index]] for index in sorted_indices])
    # endregion

    # region Class Methods
    def get_initial_state(self, qubit_index: int) -> InitialStateEnum:
        return self.initial_states[qubit_index]

    def get_operation(self, qubit_id: IQubitID, connectivity: Connectivity1D, **kwargs) -> ICircuitOperation:
        # Data allocation
        initial_state: InitialStateEnum = InitialStateEnum.ZERO
        initial_state_index: int = connectivity.get_data_index(qubit_id)
        qubit_index: int = connectivity.get_index(qubit_id)

        if initial_state_index in self.initial_states:
            initial_state = self.initial_states[initial_state_index]

        if initial_state == InitialStateEnum.ZERO:
            return Identity(qubit_index, **kwargs)
        if initial_state == InitialStateEnum.ONE:
            return Rx180(qubit_index, **kwargs)
        if initial_state == InitialStateEnum.PLUS:
            return Ry90(qubit_index, **kwargs)
        if initial_state == InitialStateEnum.MINUS:
            return Rym90(qubit_index, **kwargs)
        if initial_state == InitialStateEnum.PLUS_I:
            return Rxm90(qubit_index, **kwargs)
        if initial_state == InitialStateEnum.MINUS_I:
            return Rx90(qubit_index, **kwargs)

        raise NotImplementedError(f"Initial state {initial_state} is not supported.")

    def get_operations(self, connectivity: Connectivity1D, **kwargs) -> List[ICircuitOperation]:
        return [
            self.get_operation(
                qubit_id=connectivity.get_data_element(qubit_index),
                connectivity=connectivity,
                **kwargs,
            )
            for qubit_index in self.initial_states.keys()
        ]

    @classmethod
    def from_ordered_list(cls, initial_states: List[InitialStateEnum]) -> 'InitialStateContainer':
        """
        :return: Class method constructor based on ordered array of initial state.
        Where each element index corresponds to qubit index.
        """
        return InitialStateContainer(
            initial_states={i: state for i, state in enumerate(initial_states)}
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


def get_repetition_code_connectivity(initial_state: InitialStateContainer) -> Connectivity1D:
    code_distance: int = initial_state.distance
    chain_distance: int = 2 * code_distance - 1
    connectivity: Connectivity1D = Connectivity1D.from_chain(length=chain_distance)
    return connectivity


def construct_repetition_code_circuit(initial_state: InitialStateContainer, qec_cycles: int) -> DeclarativeCircuit:
    connectivity: Connectivity1D = get_repetition_code_connectivity(initial_state=initial_state)

    result: DeclarativeCircuit = DeclarativeCircuit()
    registry: AcquisitionRegistry = result.acquisition_registry
    result.add(get_circuit_initialize_with_heralded(
        connectivity=connectivity,
        initial_state=initial_state,
        registry=registry,
    ))
    circuit_qec_with_detectors = get_circuit_qec_with_detectors(
        connectivity=connectivity,
        qec_cycles=qec_cycles,
        registry=registry,
    )
    result.add(circuit_qec_with_detectors)
    result.add(get_circuit_final_measurement(
        connectivity=connectivity,
        registry=registry,
    ))

    # Add detector operations
    for ancilla in connectivity.ancilla_qubit_indices:
        ancilla_element: IQubitID = connectivity.get_element(index=ancilla)
        involved_edges: List[IEdgeID] = connectivity.get_edges(qubit=ancilla_element)
        neighbor_a: IQubitID = involved_edges[0].get_connected_qubit_id(element=ancilla_element)
        neighbor_b: IQubitID = involved_edges[1].get_connected_qubit_id(element=ancilla_element)
        if qec_cycles > 0:
            ancilla_reference_offset: int = (get_last_acquisition_operation(
                circuit_qec_with_detectors).circuit_level_acquisition_index + 1) - get_last_acquisition_operation(
                circuit_qec_with_detectors, qubit_index=ancilla).circuit_level_acquisition_index
        else:
            ancilla_reference_offset = (get_last_acquisition_operation(
                result).circuit_level_acquisition_index + 1) - get_last_acquisition_operation(result, qubit_index=ancilla).circuit_level_acquisition_index

        result.add(DetectorOperation(
            qubit_index=ancilla,
            last_acquisition_index=get_last_acquisition_operation(result).circuit_level_acquisition_index,
            main_target=get_last_acquisition_operation(result, qubit_index=connectivity.get_index(neighbor_a)).circuit_level_acquisition_index,
            secondary_target=get_last_acquisition_operation(result, qubit_index=connectivity.get_index(neighbor_b)).circuit_level_acquisition_index,
            reference_offset=ancilla_reference_offset + len(connectivity.data_qubit_indices) if qec_cycles > 0 else ancilla_reference_offset,
            secondary_offset=len(connectivity.ancilla_qubit_indices) if qec_cycles > 1 else None,
        ))
    for data in connectivity.data_qubit_indices:
        result.add(LogicalObservableOperation(
            qubit_index=data,
            last_acquisition_index=get_last_acquisition_operation(result).circuit_level_acquisition_index,
            main_target=get_last_acquisition_operation(result, qubit_index=data).circuit_level_acquisition_index
        ))
    return result


def construct_repetition_code_circuit_simplified(initial_state: InitialStateContainer, qec_cycles: int) -> DeclarativeCircuit:
    connectivity: Connectivity1D = get_repetition_code_connectivity(initial_state=initial_state)

    result: DeclarativeCircuit = DeclarativeCircuit()
    registry: AcquisitionRegistry = result.acquisition_registry
    result.add(get_circuit_initialize(
        connectivity=connectivity,
        initial_state=initial_state,
    ))
    cycle_circuit: DeclarativeCircuit = DeclarativeCircuit(
        repetition_strategy=FixedRepetitionStrategy(repetitions=qec_cycles)
    )
    cycle_circuit.add(get_circuit_qec_round_with_dynamical_decoupling(
        connectivity=connectivity,
        registry=registry
    ))

    result.add(cycle_circuit)
    result.add(get_circuit_final_measurement(
        connectivity=connectivity,
        registry=registry,
    ))
    return result


def get_circuit_initialize(connectivity: Connectivity1D, initial_state: InitialStateContainer) -> DeclarativeCircuit:
    result: DeclarativeCircuit = DeclarativeCircuit()
    qubit_indices: List[int] = connectivity.qubit_indices
    result.add(Barrier(qubit_indices))
    for operation in initial_state.get_operations(connectivity=connectivity):
        result.add(operation)
    result.add(Barrier(qubit_indices))
    return result


def get_circuit_initialize_with_heralded(connectivity: Connectivity1D, initial_state: InitialStateContainer, registry: AcquisitionRegistry) -> DeclarativeCircuit:
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


def get_circuit_final_measurement(connectivity: Connectivity1D, registry: AcquisitionRegistry) -> DeclarativeCircuit:
    result: DeclarativeCircuit = DeclarativeCircuit()
    for data_index in connectivity.data_qubit_indices:
        result.add(DispersiveMeasure(
            data_index,
            acquisition_strategy=RegistryAcquisitionStrategy(registry),
            acquisition_tag='final',
        ))
    return result


def get_circuit_qec_round(connectivity: Connectivity1D, registry: AcquisitionRegistry) -> DeclarativeCircuit:
    result: DeclarativeCircuit = DeclarativeCircuit()

    groups = connectivity.flux_dance_indices
    ancilla_groups = connectivity.flux_dance_ancilla_indices
    ancilla_indices: List[int] = connectivity.ancilla_qubit_indices
    all_indices: List[int] = connectivity.qubit_indices

    # First part
    for qubit_index in ancilla_groups[0]: result.add(Rym90(qubit_index))
    result.add(Barrier(all_indices))
    for ancilla, data in groups[0]: result.add(CPhase(ancilla, data))
    result.add(Barrier(all_indices))
    for ancilla, data in groups[1]: result.add(CPhase(ancilla, data))
    result.add(Barrier(all_indices))
    for qubit_index in ancilla_groups[0]: result.add(Ry90(qubit_index))
    # Second part
    for qubit_index in ancilla_groups[1]: result.add(Rym90(qubit_index))
    result.add(Barrier(all_indices))
    for ancilla, data in groups[2]: result.add(CPhase(ancilla, data))
    result.add(Barrier(all_indices))
    for ancilla, data in groups[3]: result.add(CPhase(ancilla, data))
    result.add(Barrier(all_indices))
    for qubit_index in ancilla_groups[1]: result.add(Ry90(qubit_index))
    # Ancilla measurement
    result.add(Barrier(all_indices))
    for ancilla_index in ancilla_indices:
        result.add(DispersiveMeasure(
            ancilla_index,
            acquisition_strategy=RegistryAcquisitionStrategy(registry),
            acquisition_tag='parity',
        ))
    return result


def get_circuit_qec_round_with_dynamical_decoupling(connectivity: Connectivity1D, registry: AcquisitionRegistry) -> DeclarativeCircuit:
    result: DeclarativeCircuit = DeclarativeCircuit()

    groups = connectivity.flux_dance_indices
    ancilla_groups = connectivity.flux_dance_ancilla_indices
    data_indices: List[int] = connectivity.data_qubit_indices
    ancilla_indices: List[int] = connectivity.ancilla_qubit_indices
    all_indices: List[int] = connectivity.qubit_indices

    # First part
    for qubit_index in ancilla_groups[0]: result.add(Rym90(qubit_index))
    result.add(Barrier(all_indices))
    for ancilla, data in groups[0]: result.add(CPhase(ancilla, data))
    result.add(Barrier(all_indices))
    for ancilla, data in groups[1]: result.add(CPhase(ancilla, data))
    result.add(Barrier(all_indices))
    for qubit_index in ancilla_groups[0]: result.add(Ry90(qubit_index))
    # Second part
    for qubit_index in ancilla_groups[1]: result.add(Rym90(qubit_index))
    result.add(Barrier(all_indices))
    for ancilla, data in groups[2]: result.add(CPhase(ancilla, data))
    result.add(Barrier(all_indices))
    for ancilla, data in groups[3]: result.add(CPhase(ancilla, data))
    result.add(Barrier(all_indices))
    for qubit_index in ancilla_groups[1]: result.add(Ry90(qubit_index))
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


def get_circuit_qec_with_detectors(connectivity: Connectivity1D, qec_cycles: int, registry: AcquisitionRegistry) -> DeclarativeCircuit:
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


if __name__ == '__main__':
    from qce_circuit.visualization.visualize_circuit.display_circuit import plot_circuit
    import matplotlib.pyplot as plt
    from qce_circuit.addon_stim import to_stim

    initial_state: InitialStateContainer = InitialStateContainer.from_ordered_list([
        InitialStateEnum.ZERO,
        InitialStateEnum.ONE,
        InitialStateEnum.ZERO,
        InitialStateEnum.ONE,
        InitialStateEnum.ZERO,
    ])
    circuit = construct_repetition_code_circuit(
        initial_state=initial_state,
        qec_cycles=6,
    )
    print(initial_state.as_array)
    plot_circuit(circuit)
    plt.show()

    stim_circuit = to_stim(circuit)
    print(stim_circuit.diagram())

