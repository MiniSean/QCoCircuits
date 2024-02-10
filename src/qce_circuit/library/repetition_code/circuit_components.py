# -------------------------------------------
# Module containing circuit components for constructing full repetition-code circuit.
# -------------------------------------------
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, Union, Optional
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException
from qce_circuit import (
    DeclarativeCircuit,
    Barrier,
    AcquisitionRegistry,
    Reset,
    DispersiveMeasure,
    RegistryAcquisitionStrategy,
    Rym90,
    CPhase,
    Ry90,
    FixedDurationStrategy,
    Wait,
    Rx180,
    FixedRepetitionStrategy,
)
from qce_circuit.language import InitialStateContainer
from qce_circuit.addon_stim.circuit_operations import DetectorOperation, CoordinateShiftOperation
from qce_circuit.connectivity import (
    IConnectivityLayer,
    IFluxDanceLayer,
    IQubitID,
    IEdgeID,
    EdgeIDObj,
    FluxDanceLayer,
    QubitIDObj,
)
from qce_circuit.structure.intrf_acquisition_operation import IAcquisitionOperation
from qce_circuit.structure.intrf_circuit_operation import ICircuitOperation
from qce_circuit.utilities.custom_exceptions import ElementNotIncludedException


class IRepetitionCodeConnectivity(ABC):
    """
    Interface class, describing methods and properties for repetition-code circuit connectivity.
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
    def gate_sequence_layer(self) -> IFluxDanceLayer:
        """:return: Component containing gate-sequences."""
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
    # endregion


@dataclass(frozen=True)
class Connectivity1D(IConnectivityLayer, IFluxDanceLayer):
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
    def flux_dances(self) -> List[FluxDanceLayer]:
        """:return: Array-like of flux dances."""
        edges: List[IEdgeID] = self.edge_ids
        return [
            FluxDanceLayer(
                _edge_ids=_edges
            )
            for _edges in [edges[i::4] for i in range(4)] if len(_edges) > 0
        ]

    @property
    def flux_dance_count(self) -> int:
        """:return: Number of flux-dances in layer."""
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
        for flux_dance_index in range(self.flux_dance_count):
            group = []
            for edge_id in self.get_flux_dance_at_index(flux_dance_index).edge_ids:
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
            for qubit_id in self.get_flux_dance_at_index(flux_dance_index).qubit_ids:
                if qubit_id in self.ancilla_qubit_ids:
                    group_a.append(self.get_index(qubit_id))
        for flux_dance_index in [2, 3]:
            for qubit_id in self.get_flux_dance_at_index(flux_dance_index).qubit_ids:
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

    def get_flux_dance_at_index(self, index: int) -> FluxDanceLayer:
        """:return: Flux-dance object based on round index."""
        flux_dances: List[FluxDanceLayer] = self.flux_dances
        try:
            flux_dance_layer: FluxDanceLayer = flux_dances[index]
            return flux_dance_layer
        except:
            raise ElementNotIncludedException(f"Index: {index} is out of bounds for flux dance of length: {len(flux_dances)}.")

    def get_flux_dance_from_element(self, element: IEdgeID) -> FluxDanceLayer:
        """:return: Flux-dance layer of which edge element is part of."""
        flux_dances: List[FluxDanceLayer] = self.flux_dances
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

    def get_operations(self, initial_state: InitialStateContainer, **kwargs) -> List[ICircuitOperation]:
        return [
            initial_state.get_operation(
                qubit_index=self.get_data_index(self.get_data_element(initial_state_index)),
                initial_state_index=initial_state_index,
                **kwargs,
            )
            for initial_state_index in initial_state.initial_states.keys()
        ]

    @classmethod
    def from_chain(cls, length: int) -> 'Connectivity1D':
        """:return: Class method constructor based on chain length."""
        return Connectivity1D(
            _qubit_ids=[QubitIDObj(f'D{i}') for i in range(length)]
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


def get_circuit_initialize(connectivity: Connectivity1D, initial_state: InitialStateContainer) -> DeclarativeCircuit:
    result: DeclarativeCircuit = DeclarativeCircuit()
    qubit_indices: List[int] = connectivity.qubit_indices
    result.add(Barrier(qubit_indices))
    for operation in connectivity.get_operations(initial_state=initial_state):
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
