# -------------------------------------------
# Module containing circuit components for constructing full repetition-code circuit.
# -------------------------------------------
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Callable
import numpy as np
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException, NoReferenceOperationException
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
    TwoQubitVirtualPhase,
    Barrier,
    Wait,
    DispersiveMeasure,
    VirtualPark,
)
from qce_circuit.structure.intrf_circuit_operation import (
    RelationLink,
    RelationType,
)
from qce_circuit.structure.intrf_acquisition_operation import IAcquisitionOperation
from qce_circuit.structure.intrf_circuit_operation import ICircuitOperation
from qce_circuit.structure.registry_duration import (
    IDurationStrategy,
    GlobalDurationRegistry,
    GlobalDurationRegistryManager,
    GlobalRegistryKey,
)
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
    def prepare_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of qubit-ID's for 'prepare' operation."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def measure_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of qubit-ID's for 'measure' operation."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def rotation_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of qubit-ID's for 'rotation' (gate) operation."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def detector_qubit_ids(self) -> List[IQubitID]:
        """
        :return: sub-set of qubit-ID's for 'detector' operation.
        Mainly used by STIM decoding
        """
        raise InterfaceMethodException

    @property
    @abstractmethod
    def observable_qubit_ids(self) -> List[IQubitID]:
        """
        :return: sub-set of qubit-ID's for 'observable' operation.
        Mainly used by STIM decoding
        """
        raise InterfaceMethodException

    @property
    @abstractmethod
    def calibration_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of qubit-ID's for 'state-calibration' operation."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def gate_sequences(self) -> List[GateSequenceLayer]:
        """:return: Array-like of gate sequences."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def contains_qubit_refocusing(self) -> bool:
        """
        :return: Boolean, whether QEC-cycle contains qubit refocusing gates.
        (X-gates during Ancilla measurement block).
        """
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
    def prepare_qubit_indices(self) -> List[int]:
        """:return: sub-set of qubit-indices for 'prepare' operation."""
        return [self.map_qubit_id_to_circuit_index(qubit_id) for qubit_id in self.prepare_qubit_ids]

    @property
    def measure_qubit_indices(self) -> List[int]:
        """:return: sub-set of qubit-indices for 'measure' operation."""
        return [self.map_qubit_id_to_circuit_index(qubit_id) for qubit_id in self.measure_qubit_ids]

    @property
    def measure_data_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of Data-qubit-ID's for 'measure' operation."""
        return [qubit_id for qubit_id in self.measure_qubit_ids if qubit_id in self.data_qubit_ids]

    @property
    def measure_ancilla_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of Ancilla-qubit-ID's for 'measure' operation."""
        return [qubit_id for qubit_id in self.measure_qubit_ids if qubit_id in self.ancilla_qubit_ids]

    @property
    def measure_data_qubit_indices(self) -> List[int]:
        """:return: sub-set of Data-qubit-indices for 'measure' operation."""
        return [self.map_qubit_id_to_circuit_index(qubit_id) for qubit_id in self.measure_data_qubit_ids]

    @property
    def measure_ancilla_qubit_indices(self) -> List[int]:
        """:return: sub-set of Ancilla-qubit-indices for 'measure' operation."""
        return [self.map_qubit_id_to_circuit_index(qubit_id) for qubit_id in self.measure_ancilla_qubit_ids]

    @property
    def rotation_data_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of Data-qubit-ID's for 'rotation' (gate) operation."""
        return [qubit_id for qubit_id in self.rotation_qubit_ids if qubit_id in self.data_qubit_ids]

    @property
    def rotation_ancilla_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of Ancilla-qubit-ID's for 'rotation' (gate) operation."""
        return [qubit_id for qubit_id in self.rotation_qubit_ids if qubit_id in self.ancilla_qubit_ids]

    @property
    def rotation_data_qubit_indices(self) -> List[int]:
        """:return: sub-set of Data-qubit-indices for 'rotation' (gate) operation."""
        return [self.map_qubit_id_to_circuit_index(qubit_id) for qubit_id in self.rotation_data_qubit_ids]

    @property
    def rotation_ancilla_qubit_indices(self) -> List[int]:
        """:return: sub-set of Ancilla-qubit-indices for 'rotation' (gate) operation."""
        return [self.map_qubit_id_to_circuit_index(qubit_id) for qubit_id in self.rotation_ancilla_qubit_ids]

    @property
    def gate_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of qubit-ID's for 'fluxed' (2-qubit gate) operation."""
        result: List[IQubitID] = []
        for sequence_layer in self.gate_sequences:
            for gate_operation in sequence_layer.gate_operations:
                for qubit_id in gate_operation.identifier.qubit_ids:
                    if qubit_id not in result:
                        result.append(qubit_id)

        return result

    @property
    def gate_data_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of Data-qubit-ID's for 'fluxed' (2-qubit gate) operation."""
        return [qubit_id for qubit_id in self.gate_qubit_ids if qubit_id in self.data_qubit_ids]

    @property
    def gate_ancilla_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of Ancilla-qubit-ID's for 'fluxed' (2-qubit gate) operation."""
        return [qubit_id for qubit_id in self.gate_qubit_ids if qubit_id in self.ancilla_qubit_ids]

    @property
    def gate_data_qubit_indices(self) -> List[int]:
        """:return: sub-set of Data-qubit-indices for 'fluxed' (2-qubit gate) operation."""
        return [self.map_qubit_id_to_circuit_index(qubit_id) for qubit_id in self.gate_data_qubit_ids]

    @property
    def gate_ancilla_qubit_indices(self) -> List[int]:
        """:return: sub-set of Ancilla-qubit-indices for 'fluxed' (2-qubit gate) operation."""
        return [self.map_qubit_id_to_circuit_index(qubit_id) for qubit_id in self.gate_ancilla_qubit_ids]

    @property
    def park_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of qubit-ID's for 'fluxed' (parking) operation."""
        result: List[IQubitID] = []
        for sequence_layer in self.gate_sequences:
            for park_operation in sequence_layer.park_operations:
                if park_operation.identifier not in result:
                    result.append(park_operation.identifier)

        return result

    @property
    def park_data_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of Data-qubit-ID's for 'fluxed' (parking) operation."""
        return [qubit_id for qubit_id in self.park_qubit_ids if qubit_id in self.data_qubit_ids]

    @property
    def park_ancilla_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of Ancilla-qubit-ID's for 'fluxed' (parking) operation."""
        return [qubit_id for qubit_id in self.park_qubit_ids if qubit_id in self.ancilla_qubit_ids]

    @property
    def park_data_qubit_indices(self) -> List[int]:
        """:return: sub-set of Data-qubit-indices for 'fluxed' (parking) operation."""
        return [self.map_qubit_id_to_circuit_index(qubit_id) for qubit_id in self.park_data_qubit_ids]

    @property
    def park_ancilla_qubit_indices(self) -> List[int]:
        """:return: sub-set of Ancilla-qubit-indices for 'fluxed' (parking) operation."""
        return [self.map_qubit_id_to_circuit_index(qubit_id) for qubit_id in self.park_ancilla_qubit_ids]

    @property
    def detector_qubit_indices(self) -> List[int]:
        """
        :return: sub-set of qubit-indices for 'detector' operation.
        Mainly used by STIM decoding
        """
        return [self.map_qubit_id_to_circuit_index(qubit_id) for qubit_id in self.detector_qubit_ids]

    @property
    def observable_qubit_indices(self) -> List[int]:
        """
        :return: sub-set of qubit-indices for 'observable' operation.
        Mainly used by STIM decoding
        """
        return [self.map_qubit_id_to_circuit_index(qubit_id) for qubit_id in self.observable_qubit_ids]

    @property
    def calibration_qubit_indices(self) -> List[int]:
        """:return: sub-set of qubit-indices for 'state-calibration' operation."""
        return [self.map_qubit_id_to_circuit_index(qubit_id) for qubit_id in self.calibration_qubit_ids]

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
        for qubit_id in self.qubit_ids:
            if self.map_qubit_id_to_circuit_index(qubit_id=qubit_id) == index:
                return qubit_id
        raise ValueError(f'Index {index} does not point to any element. Try self.map_qubit_id_to_circuit_index.')

    def get_index(self, element: IQubitID) -> int:
        """:return: Index corresponding to Qubit-ID element."""
        return self.map_qubit_id_to_circuit_index(qubit_id=element)

    def get_edges(self, qubit_id: IQubitID) -> List[IEdgeID]:
        """:return: All qubit-to-qubit edges from qubit-ID."""
        result: List[IEdgeID] = []
        edge_ids: List[IEdgeID] = unique_in_order([identifier for sequence in self.gate_sequences for identifier in sequence.edge_ids])
        for edge in edge_ids:
            if edge.contains(element=qubit_id):
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

    def get_park_sequence_indices(self, sequence_index: int) -> Optional[List[int]]:
        """
        :param sequence_index: Gate sequence index. If index is out of range, return None.
        :return: (Optional) Array-like of integers corresponding qubit-circuit index.
        """
        # Guard clause, if index is out of range, return None.
        if not 0 <= sequence_index < len(self.gate_sequences):
            return None

        sequence: GateSequenceLayer = self.gate_sequences[sequence_index]
        result: List[int] = []
        for park_operation in sequence.park_operations:
            if park_operation.identifier not in self.qubit_ids:
                continue
            result.append(
                self.map_qubit_id_to_circuit_index(park_operation.identifier),
            )
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

        ancilla_ids: List[IQubitID] = self.rotation_ancilla_qubit_ids
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
    _qubit_refocusing: bool = field(default=True)
    """Boolean describing qubit refocusing operation each QEC-cycle."""

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
    def prepare_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of qubit-ID's for 'prepare' operation."""
        return self.qubit_ids

    @property
    def measure_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of qubit-ID's for 'measure' operation."""
        return self.qubit_ids

    @property
    def rotation_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of qubit-ID's for 'rotation' (gate) operation."""
        return self.qubit_ids

    @property
    def detector_qubit_ids(self) -> List[IQubitID]:
        """
        :return: sub-set of qubit-ID's for 'detector' operation.
        Mainly used by STIM decoding
        """
        return self.ancilla_qubit_ids

    @property
    def observable_qubit_ids(self) -> List[IQubitID]:
        """
        :return: sub-set of qubit-ID's for 'observable' operation.
        Mainly used by STIM decoding
        """
        return self.data_qubit_ids

    @property
    def calibration_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of qubit-ID's for 'state-calibration' operation."""
        return self.qubit_ids

    @property
    def gate_sequences(self) -> List[GateSequenceLayer]:
        """:return: Array-like of gate sequences."""
        return self._gate_sequences

    @property
    def contains_qubit_refocusing(self) -> bool:
        """
        :return: Boolean, whether QEC-cycle contains qubit refocusing gates.
        (X-gates during Ancilla measurement block).
        """
        return self._qubit_refocusing
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
    def get_channel_order_and_mapping(self) -> Tuple[List[int], Dict[int, str]]:
        """:return: Tuple of channel order and mapping based on sorting qubit-ID's in increasing order."""
        return CompositeRepetitionCodeDescription.channel_order_and_mapping(
            involved_qubit_ids=self.qubit_ids,
            mapping=self.map_qubit_id_to_circuit_index,
        )

    @classmethod
    def from_chain(cls, length: int, qubit_refocusing: bool = True) -> 'RepetitionCodeDescription':
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
            _qubit_refocusing=qubit_refocusing,
        )

    @classmethod
    def from_initial_state(cls, initial_state: InitialStateContainer, qubit_refocusing: bool = True) -> 'RepetitionCodeDescription':
        """:return: Class method constructor based on initial data-qubit state."""
        code_distance: int = initial_state.distance
        chain_distance: int = 2 * code_distance - 1
        return RepetitionCodeDescription.from_chain(length=chain_distance, qubit_refocusing=qubit_refocusing)

    @classmethod
    def from_connectivity(cls, involved_qubit_ids: List[IQubitID], connectivity: IGenericSurfaceCodeLayer, qubit_index_map: Optional[Dict[IQubitID, int]] = None, qubit_refocusing: bool = True) -> 'RepetitionCodeDescription':
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
            else:
                gate_sequences.append(GateSequenceLayer.empty())
        # Setup default qubit index map
        if qubit_index_map is None:
            qubit_index_map: Dict[IQubitID, int] = {qubit_id: i for i, qubit_id in enumerate(involved_qubit_ids)}
        # Return constructed connectivity
        return RepetitionCodeDescription(
            _data_qubit_ids=data_qubit_ids,
            _ancilla_qubit_ids=ancilla_qubit_ids,
            _gate_sequences=gate_sequences,
            _qubit_index_map=qubit_index_map,
            _qubit_refocusing=qubit_refocusing,
        )
    # endregion


@dataclass(frozen=True)
class CompositeRepetitionCodeDescription(IRepetitionCodeDescription):
    """
    Data class, describing code description based on a default description.
    Adds (optional) leading components which inform the complete description to uses Readout, 1QG, 2QG, Parking from different (leading) descriptions.
    Adds (optional) exclusion components which force the exclusion of certain Readout, 1QG, 2QG, Parking operations (qubit-ID) based.
    """
    _base_description: IRepetitionCodeDescription
    _qubit_index_map: Dict[IQubitID, int]
    """Mapping from Qubit-ID to circuit channel index."""
    _connectivity: IGenericSurfaceCodeLayer
    """Connectivity layer used for determining dynamic parking operations."""
    _leading_readout_description: Optional[IRepetitionCodeDescription] = field(default=None)
    _leading_gate_description: Optional[IRepetitionCodeDescription] = field(default=None)
    _exclude_readout_qubit_ids: List[IQubitID] = field(default_factory=list)
    _exclude_rotation_qubit_ids: List[IQubitID] = field(default_factory=list)
    _exclude_gate_edge_ids: List[IEdgeID] = field(default_factory=list)
    _exclude_gate_qubit_ids: List[IQubitID] = field(default_factory=list)
    _only_required_parking_operations: bool = field(default=False)

    # region Interface Properties
    @property
    def qubit_ids(self) -> List[IQubitID]:
        """:return: (All) qubit-ID's in connectivity."""
        result: List[IQubitID] = self._base_description.qubit_ids
        # Add all qubit-ID's from (optional) readout description
        if self._leading_readout_description is not None:
            for _qubit_id in self._leading_readout_description.qubit_ids:
                if _qubit_id not in result:
                    result.append(_qubit_id)
        # Add all qubit-ID's from (optional) gate description
        if self._leading_gate_description is not None:
            for _qubit_id in self._leading_gate_description.qubit_ids:
                if _qubit_id not in result:
                    result.append(_qubit_id)
        return result

    @property
    def data_qubit_ids(self) -> List[IQubitID]:
        """:return: (All) Data-qubit-ID's in connectivity."""
        return self._base_description.data_qubit_ids

    @property
    def ancilla_qubit_ids(self) -> List[IQubitID]:
        """:return: (All) Ancilla-qubit-ID's in connectivity."""
        return self._base_description.ancilla_qubit_ids

    @property
    def prepare_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of qubit-ID's for 'prepare' operation."""
        return self.measure_qubit_ids

    @property
    def measure_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of qubit-ID's for 'measure' operation."""
        return self.measure_ancilla_qubit_ids + self.measure_data_qubit_ids

    @property
    def measure_data_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of Data-qubit-ID's for 'measure' operation."""
        result: List[IQubitID] = self._base_description.measure_data_qubit_ids
        if self._leading_readout_description is not None:
            result = self._leading_readout_description.measure_data_qubit_ids
        return [qubit_id for qubit_id in result if qubit_id not in self._exclude_readout_qubit_ids]

    @property
    def measure_ancilla_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of Ancilla-qubit-ID's for 'measure' operation."""
        result: List[IQubitID] = self._base_description.measure_ancilla_qubit_ids
        if self._leading_readout_description is not None:
            result = self._leading_readout_description.measure_ancilla_qubit_ids
        return [qubit_id for qubit_id in result if qubit_id not in self._exclude_readout_qubit_ids]

    @property
    def rotation_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of qubit-ID's for 'rotation' (gate) operation."""
        result: List[IQubitID] = self._base_description.rotation_qubit_ids
        if self._leading_gate_description is not None:
            result = self._leading_gate_description.rotation_qubit_ids
        return [qubit_id for qubit_id in result if qubit_id not in self._exclude_rotation_qubit_ids]

    @property
    def rotation_data_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of Data-qubit-ID's for 'rotation' (gate) operation."""
        result: List[IQubitID] = self._base_description.rotation_data_qubit_ids
        if self._leading_gate_description is not None:
            result = self._leading_gate_description.rotation_data_qubit_ids
        return [qubit_id for qubit_id in result if qubit_id not in self._exclude_rotation_qubit_ids]

    @property
    def rotation_ancilla_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of Ancilla-qubit-ID's for 'rotation' (gate) operation."""
        result: List[IQubitID] = self._base_description.rotation_ancilla_qubit_ids
        if self._leading_gate_description is not None:
            result = self._leading_gate_description.rotation_ancilla_qubit_ids
        return [qubit_id for qubit_id in result if qubit_id not in self._exclude_rotation_qubit_ids]

    @property
    def detector_qubit_ids(self) -> List[IQubitID]:
        """
        :return: sub-set of qubit-ID's for 'detector' operation.
        Mainly used by STIM decoding
        """
        return self._base_description.detector_qubit_ids

    @property
    def observable_qubit_ids(self) -> List[IQubitID]:
        """
        :return: sub-set of qubit-ID's for 'observable' operation.
        Mainly used by STIM decoding
        """
        return self._base_description.observable_qubit_ids

    @property
    def calibration_qubit_ids(self) -> List[IQubitID]:
        """:return: sub-set of qubit-ID's for 'state-calibration' operation."""
        return self.measure_qubit_ids

    @property
    def gate_sequences(self) -> List[GateSequenceLayer]:
        """:return: Array-like of gate sequences."""
        base_gate_sequence: List[GateSequenceLayer] = self._base_description.gate_sequences
        if self._leading_gate_description is not None:
            base_gate_sequence = self._leading_gate_description.gate_sequences

        result: List[GateSequenceLayer] = []
        # Filtered gate-sequence
        for _gate_sequence in base_gate_sequence:
            # Filtered gate operations
            filtered_gate_operations: List[Operation[IEdgeID]] = []
            for operation in _gate_sequence.gate_operations:
                if operation.identifier in self._exclude_gate_edge_ids:
                    continue
                if any([_qubit_id in self._exclude_gate_qubit_ids for _qubit_id in operation.identifier.qubit_ids]):
                    continue
                filtered_gate_operations.append(operation)

            # Force only required parking operations
            filtered_park_operations: List[Operation[IQubitID]] = _gate_sequence.park_operations
            if self._only_required_parking_operations:
                edge_identifiers: List[IEdgeID] = [element.identifier for element in filtered_gate_operations]
                filtered_park_operations = [Operation.type_park(element) for element in self._connectivity.qubit_ids if get_requires_parking(element=element, edge_ids=edge_identifiers, connectivity=self._connectivity)]

            result.append(GateSequenceLayer(
                _park_operations=filtered_park_operations,
                _gate_operations=filtered_gate_operations,
            ))
        return result

    @property
    def contains_qubit_refocusing(self) -> bool:
        """
        :return: Boolean, whether QEC-cycle contains qubit refocusing gates.
        (X-gates during Ancilla measurement block).
        """
        return self._base_description.contains_qubit_refocusing
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

    def get_active_ancilla_indices(self, sequence_index: int) -> Optional[List[int]]:
        """
        Determines which ancilla indices need to be 'active' for a given sequence index.
        :param sequence_index: Gate sequence index. If index is out of range, return None.
        :return: (Optional) Array-like of single-integer (corresponding to ancilla-index).
        """
        leading_gate_sequences: List[GateSequenceLayer] = self._base_description.gate_sequences
        if self._leading_gate_description is not None:
            leading_gate_sequences = self._leading_gate_description.gate_sequences

        # Guard clause, if index is out of range, return None.
        if not 0 <= sequence_index < len(leading_gate_sequences):
            return None

        ancilla_ids: List[IQubitID] = self.rotation_ancilla_qubit_ids
        sequence: GateSequenceLayer = leading_gate_sequences[sequence_index]
        result: List[int] = []
        for edge in sequence.edge_ids:
            for qubit_id in edge.qubit_ids:
                if qubit_id in ancilla_ids:
                    result.append(self.map_qubit_id_to_circuit_index(qubit_id))
        return result
    # endregion

    # region Class Methods
    def get_channel_order_and_mapping(self) -> Tuple[List[int], Dict[int, str]]:
        """:return: Tuple of channel order and mapping based on sorting qubit-ID's in increasing order."""
        return CompositeRepetitionCodeDescription.channel_order_and_mapping(
            involved_qubit_ids=self.qubit_ids,
            mapping=self.map_qubit_id_to_circuit_index,
        )
    # endregion

    # region Static Class Methods
    @staticmethod
    def channel_order_and_mapping(involved_qubit_ids: List[IQubitID], mapping: Callable[[IQubitID], int]) -> Tuple[List[int], Dict[int, str]]:
        """:return: Tuple of channel order and mapping based on sorting qubit-ID's in increasing order."""
        involved_indices = [mapping(qubit_id) for qubit_id in involved_qubit_ids]

        # Step 1: Get the sort order of the first list
        sort_order = sorted(range(len(involved_qubit_ids)), key=lambda x: involved_qubit_ids[x].id)
        # Step 2: Apply this sort order to both lists
        involved_qubit_ids = [involved_qubit_ids[i] for i in sort_order]
        involved_indices = [involved_indices[i] for i in sort_order]

        channel_order = involved_indices
        channel_map = {i: qubit_id.id for i, qubit_id in zip(involved_indices, involved_qubit_ids)}
        return channel_order, channel_map
    # endregion


@dataclass(frozen=True)
class GlobalDecouplingWaitDurationStrategy(IDurationStrategy):
    """
    Data class, implementing IDurationStrategy interface.
    Exposes wait duration during dynamical decoupling based on global duration settings.
    """
    _registry: GlobalDurationRegistry = field(default_factory=GlobalDurationRegistryManager.read_config, compare=False, repr=False)

    # region Interface Properties
    def get_variable_duration(self, task: ICircuitOperation) -> float:
        """:return: Duration [ns]."""
        global_readout_duration: float = self._registry.get_registry_at(key=GlobalRegistryKey.READOUT)
        global_microwave_duration: float = self._registry.get_registry_at(key=GlobalRegistryKey.MICROWAVE)
        return max(0.0, 0.5 * (global_readout_duration - global_microwave_duration))
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
    for qubit_index in connectivity.prepare_qubit_indices:
        result.add(Reset(qubit_index))
    for qubit_index in connectivity.measure_qubit_indices:
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
    for data_index in connectivity.measure_data_qubit_indices:
        result.add(DispersiveMeasure(
            data_index,
            acquisition_strategy=RegistryAcquisitionStrategy(registry),
            acquisition_tag='final',
        ))
    return result


def get_circuit_qec_round(connectivity: IRepetitionCodeDescription, registry: AcquisitionRegistry) -> DeclarativeCircuit:
    result: DeclarativeCircuit = DeclarativeCircuit()

    all_indices: List[int] = connectivity.qubit_indices
    current_active_ancilla_indices: List[int] = []

    for sequence_index in range(connectivity.gate_sequence_count):
        # Check if ancilla's need to be 'activated'
        sequence_active_ancilla_indices: List[int] = connectivity.get_active_ancilla_indices(sequence_index)
        next_sequence_active_ancilla_indices: Optional[List[int]] = connectivity.get_active_ancilla_indices(sequence_index + 1)
        sequence_active_gate_indices: List[Tuple[int, int]] = connectivity.get_gate_sequence_indices(sequence_index)
        sequence_active_park_indices: List[int] = connectivity.get_park_sequence_indices(sequence_index)

        require_activation: List[int] = [qubit_index for qubit_index in sequence_active_ancilla_indices if qubit_index not in current_active_ancilla_indices]
        require_closure: List[int] = sequence_active_ancilla_indices
        if next_sequence_active_ancilla_indices is not None:
            require_closure = [qubit_index for qubit_index in sequence_active_ancilla_indices if qubit_index not in next_sequence_active_ancilla_indices]
        # Update current active ancilla indices
        current_active_ancilla_indices = sequence_active_ancilla_indices

        # Schedule Ancilla basis rotation for 'activation'
        for qubit_index in require_activation:
            result.add(Ry90(qubit_index))
        if len(require_activation) > 0:
            result.add(Barrier(all_indices))

        # Schedule two-qubit gate
        for index0, index1 in sequence_active_gate_indices:
            result.add(CPhase(index0, index1))

        # Schedule parking operation
        for qubit_index in sequence_active_park_indices:
            result.add(VirtualPark(qubit_index))

        if len(sequence_active_gate_indices) > 0:
            result.add(Barrier(all_indices))

        # Schedule single qubit phase updates
        for index0, index1 in sequence_active_gate_indices:
            result.add(TwoQubitVirtualPhase(index0, index1))

        if len(sequence_active_gate_indices) > 0 or len(sequence_active_park_indices) > 0:
            result.add(Barrier(all_indices))

        # Schedule Ancilla basis rotation for 'closure'
        for qubit_index in require_closure:
            result.add(Rym90(qubit_index))

    # Ancilla measurement
    result.add(Barrier(all_indices))
    for ancilla_index in connectivity.measure_ancilla_qubit_indices:
        result.add(DispersiveMeasure(
            ancilla_index,
            acquisition_strategy=RegistryAcquisitionStrategy(registry),
            acquisition_tag='parity',
        ))
    return result


def get_circuit_qec_round_with_dynamical_decoupling(connectivity: IRepetitionCodeDescription, registry: AcquisitionRegistry) -> DeclarativeCircuit:
    result: DeclarativeCircuit = DeclarativeCircuit()

    all_indices: List[int] = connectivity.qubit_indices
    current_active_ancilla_indices: List[int] = []

    for sequence_index in range(connectivity.gate_sequence_count):
        # Check if ancilla's need to be 'activated'
        sequence_active_ancilla_indices: List[int] = connectivity.get_active_ancilla_indices(sequence_index)
        next_sequence_active_ancilla_indices: Optional[List[int]] = connectivity.get_active_ancilla_indices(sequence_index + 1)
        sequence_active_gate_indices: List[Tuple[int, int]] = connectivity.get_gate_sequence_indices(sequence_index)
        sequence_active_park_indices: List[int] = connectivity.get_park_sequence_indices(sequence_index)

        require_activation: List[int] = [qubit_index for qubit_index in sequence_active_ancilla_indices if qubit_index not in current_active_ancilla_indices]
        require_closure: List[int] = sequence_active_ancilla_indices
        if next_sequence_active_ancilla_indices is not None:
            require_closure = [qubit_index for qubit_index in sequence_active_ancilla_indices if qubit_index not in next_sequence_active_ancilla_indices]
        # Update current active ancilla indices
        current_active_ancilla_indices = sequence_active_ancilla_indices

        # Schedule Ancilla basis rotation for 'activation'
        for qubit_index in require_activation:
            result.add(Ry90(qubit_index))
        if len(require_activation) > 0:
            result.add(Barrier(all_indices))

        # Schedule two-qubit gate
        for index0, index1 in sequence_active_gate_indices:
            result.add(CPhase(index0, index1))

        # Schedule parking operation
        for qubit_index in sequence_active_park_indices:
            result.add(VirtualPark(qubit_index))

        if len(sequence_active_gate_indices) > 0:
            result.add(Barrier(all_indices))

        # Schedule single qubit phase updates
        for index0, index1 in sequence_active_gate_indices:
            result.add(TwoQubitVirtualPhase(index0, index1))

        if len(sequence_active_gate_indices) > 0 or len(sequence_active_park_indices) > 0:
            result.add(Barrier(all_indices))

        # Schedule Ancilla basis rotation for 'closure'
        for qubit_index in require_closure:
            result.add(Rym90(qubit_index))

    # Ancilla measurement
    result.add(Barrier(all_indices))
    for ancilla_index in connectivity.measure_ancilla_qubit_indices:
        result.add(DispersiveMeasure(
            ancilla_index,
            acquisition_strategy=RegistryAcquisitionStrategy(registry),
            acquisition_tag='parity',
        ))
    dynamical_decoupling_wait = GlobalDecouplingWaitDurationStrategy()
    for data_index in connectivity.rotation_data_qubit_indices:
        result.add(Wait(data_index, duration_strategy=dynamical_decoupling_wait))
        result.add(Rx180(data_index))
        result.add(Wait(data_index, duration_strategy=dynamical_decoupling_wait))
    result.add(Barrier(all_indices))
    return result


def get_circuit_qec_round_with_dynamical_decoupling_simplified(connectivity: IRepetitionCodeDescription, registry: AcquisitionRegistry) -> DeclarativeCircuit:
    """
    :return: DeclarativeCircuit containing (repetition-code) QEC-cycle with dynamical decoupling.
    Prioritizes (simplified) readability over operation accuracy. (Neglecting exact circuit implementation)
    """
    result: DeclarativeCircuit = DeclarativeCircuit()

    current_active_ancilla_indices: List[int] = []

    relation_activation = RelationLink.no_relation()
    for sequence_index in range(connectivity.gate_sequence_count):
        # Check if ancilla's need to be 'activated'
        sequence_active_ancilla_indices: List[int] = connectivity.get_active_ancilla_indices(sequence_index)
        next_sequence_active_ancilla_indices: Optional[List[int]] = connectivity.get_active_ancilla_indices(sequence_index + 1)
        sequence_active_gate_indices: List[Tuple[int, int]] = connectivity.get_gate_sequence_indices(sequence_index)
        sequence_active_park_indices: List[int] = connectivity.get_park_sequence_indices(sequence_index)

        require_activation: List[int] = [qubit_index for qubit_index in sequence_active_ancilla_indices if qubit_index not in current_active_ancilla_indices]
        require_closure: List[int] = sequence_active_ancilla_indices
        if next_sequence_active_ancilla_indices is not None:
            require_closure = [qubit_index for qubit_index in sequence_active_ancilla_indices if qubit_index not in next_sequence_active_ancilla_indices]
        # Update current active ancilla indices
        current_active_ancilla_indices = sequence_active_ancilla_indices

        # Schedule Ancilla basis rotation for 'activation'
        for qubit_index in require_activation:
            result.add(Ry90(qubit_index, relation=relation_activation))
        try:
            relation_parking = RelationLink(result.get_last_entry(), RelationType.FOLLOWED_BY)
        except NoReferenceOperationException:
            relation_parking = RelationLink.no_relation()

        # Schedule two-qubit gate
        for index0, index1 in sequence_active_gate_indices:
            result.add(CPhase(index0, index1, relation=relation_parking))
        # Schedule parking operation
        for qubit_index in sequence_active_park_indices:
            result.add(VirtualPark(qubit_index, relation=relation_parking))

        try:
            relation_activation = RelationLink(result.get_last_entry(), RelationType.FOLLOWED_BY)
        except NoReferenceOperationException:
            relation_activation = RelationLink.no_relation()

        # Schedule Ancilla basis rotation for 'closure'
        for qubit_index in require_closure:
            result.add(Rym90(qubit_index, relation=relation_activation))

    # Ancilla measurement
    # result.add(Barrier(all_indices))
    relation = RelationLink(result.get_last_entry(), RelationType.FOLLOWED_BY)
    for ancilla_index in connectivity.measure_ancilla_qubit_indices:
        result.add(DispersiveMeasure(
            ancilla_index,
            acquisition_strategy=RegistryAcquisitionStrategy(registry),
            acquisition_tag='parity',
            relation=relation,
        ))
    dynamical_decoupling_wait = GlobalDecouplingWaitDurationStrategy()
    for data_index in connectivity.rotation_data_qubit_indices:
        result.add(Wait(data_index, duration_strategy=dynamical_decoupling_wait, relation=relation))
        result.add(Rx180(data_index))
        result.add(Wait(data_index, duration_strategy=dynamical_decoupling_wait))
    return result


def get_circuit_qec_with_detectors(connectivity: IRepetitionCodeDescription, qec_cycles: int, registry: AcquisitionRegistry) -> DeclarativeCircuit:
    result: DeclarativeCircuit = DeclarativeCircuit()
    # Guard clause, if qec-cycles is 0, return empty circuit
    if qec_cycles == 0:
        for ancilla_index in connectivity.measure_ancilla_qubit_indices:
            result.add(DispersiveMeasure(
                ancilla_index,
                acquisition_strategy=RegistryAcquisitionStrategy(registry),
                acquisition_tag='final',
            ))
        return result

    all_indices: List[int] = connectivity.qubit_indices
    ancilla_indices: List[int] = connectivity.detector_qubit_indices
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
        second_sub_circuit.add(Barrier(qubit_indices=all_indices))
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
