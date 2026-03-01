# -------------------------------------------
# Module containing interface and implementation of generic (Surface17) gate sequences.
# -------------------------------------------
import warnings
from abc import ABC, ABCMeta, abstractmethod
from typing import List, Union, Optional, Dict
from qce_circuit.utilities.custom_exceptions import (
    ElementNotIncludedException,
    InterfaceMethodException,
)
from qce_circuit.utilities.array_manipulation import unique_in_order
from qce_circuit.connectivity.intrf_channel_identifier import (
    IQubitID,
    IEdgeID,
    IFeedlineID,
)
from qce_circuit.connectivity.intrf_connectivity_surface_code import (
    ISurfaceCodeLayer,
    IParityGroup,
    FrequencyGroupIdentifier,
    StabilizerType,
)
from qce_circuit.connectivity.intrf_connectivity_gate_sequence import (
    IGateSequenceLayer,
    GateSequenceLayer,
)
from qce_circuit.connectivity.connectivity_surface_code import Surface17Layer


class ILogicalObservable(ABC):
    """
    Interface class, describing logical observable.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def observable_basis(self) -> StabilizerType:
        """:return: (StabilizerType) basis of logical observable."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def involved_data_qubit_ids(self) -> List[IQubitID]:
        """:return: Array-like of data-qubit ID's involved in observable."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def concordant_stabilizer_qubit_ids(self) -> List[IQubitID]:
        """
        :return: Array-like of ancilla-qubit ID's that describe the stabilizers which are concordant with the observable.
        """
        raise InterfaceMethodException
    # endregion

    # region Interface Methods
    @abstractmethod
    def contains(self, element: IQubitID) -> bool:
        """:return: True if element is contained in logical observable, else False."""
        raise InterfaceMethodException

    @abstractmethod
    def get_projection_basis(self, qubit_id: IQubitID) -> StabilizerType:
        """:return: Projection basis per qubit in observable."""
        raise InterfaceMethodException
    # endregion


class IGenericSurfaceCodeLayer(ISurfaceCodeLayer, IGateSequenceLayer, metaclass=ABCMeta):
    """
    Interface class, combining ISurfaceCodeLayer and IGateSequenceLayer.
    """

    # region Interface Methods
    @abstractmethod
    def get_gate_sequence_indices(self, parity_group: IParityGroup) -> List[int]:
        """
        :return: Array-like of gate-sequence indices corresponding to parity-group edge-ID's.
        Returns an empty list if parity-group is not present.
        """
        raise InterfaceMethodException

    @abstractmethod
    def get_logical_observable(self, basis: StabilizerType) -> ILogicalObservable:
        """:return: Logical observable corresponding to basis."""
        raise InterfaceMethodException
    # endregion


class LogicalObservable(ILogicalObservable):
    """
    Data class, implementing ILogicalObservable interface.
    """

    # region Interface Properties
    @property
    def observable_basis(self) -> StabilizerType:
        """:return: (StabilizerType) basis of logical observable."""
        return self._observable_basis

    @property
    def involved_data_qubit_ids(self) -> List[IQubitID]:
        """:return: Array-like of data-qubit ID's involved in observable."""
        return unique_in_order(self._data_qubit_projections.keys())

    @property
    def concordant_stabilizer_qubit_ids(self) -> List[IQubitID]:
        """
        :return: Array-like of ancilla-qubit ID's that describe the stabilizers which are concordant with the observable.
        """
        return self._supporting_stabilizers
    # endregion

    # region Class Constructor
    def __init__(
            self,
            observable_basis: StabilizerType,
            data_qubit_projections: Dict[IQubitID, StabilizerType],
            supporting_stabilizers: List[IQubitID],
            default_projections: StabilizerType = StabilizerType.STABILIZER_Z,
    ):
        self._observable_basis: StabilizerType = observable_basis
        self._data_qubit_projections: Dict[IQubitID, StabilizerType] = data_qubit_projections
        self._supporting_stabilizers: List[IQubitID] = supporting_stabilizers
        self._default_projections: StabilizerType = default_projections
    # endregion

    # region Interface Methods
    def contains(self, element: IQubitID) -> bool:
        """:return: True if element is contained in logical observable, else False."""
        return element in self._data_qubit_projections

    def get_projection_basis(self, qubit_id: IQubitID) -> StabilizerType:
        """:return: Projection basis per qubit in observable."""
        if qubit_id not in self._data_qubit_projections:
            # raise ObservableElementNotIncludedException(f"{qubit_id} is not in logical observable. Use one of self.involved_data_qubit_ids.")
            return self._default_projections
        return self._data_qubit_projections[qubit_id]
    # endregion


class GenericSurfaceCode(IGenericSurfaceCodeLayer):

    # region IGateSequenceLayer Interface Properties
    @property
    def gate_sequence_count(self) -> int:
        """:return: Number of gate-sequences in layer."""
        return len(self._gate_sequences)

    @property
    def gate_sequences(self) -> List[GateSequenceLayer]:
        """:return: Array-like of gate sequences."""
        return self._gate_sequences

    @property
    def involved_qubit_ids(self) -> List[IQubitID]:
        """:return: (Only) involved qubit-ID's in gate sequence."""
        gate_sequence_layers: List[GateSequenceLayer] = [self.get_gate_sequence_at_index(layer_index) for layer_index in range(self.gate_sequence_count)]
        return unique_in_order([qubit_id for gate_sequence_layer in gate_sequence_layers for qubit_id in gate_sequence_layer.qubit_ids])
    # endregion

    # region ISurfaceCodeLayer Interface Properties
    @property
    def parity_group_x(self) -> List[IParityGroup]:
        """:return: (All) parity groups part of X-stabilizers."""
        return self._parity_group_x

    @property
    def parity_group_z(self) -> List[IParityGroup]:
        """:return: (All) parity groups part of Z-stabilizers."""
        return self._parity_group_z

    @property
    def data_qubit_ids(self) -> List[IQubitID]:
        """:return: (Data) qubit-ID's in device layer."""
        return unique_in_order([data_id for parity_group in self.parity_group_x + self.parity_group_z for data_id in parity_group.data_ids])

    @property
    def ancilla_qubit_ids(self) -> List[IQubitID]:
        """:return: (Ancilla) qubit-ID's in device layer."""
        return unique_in_order([parity_group.ancilla_id for parity_group in self.parity_group_x + self.parity_group_z])
    # endregion

    # region IDeviceLayer Interface Properties
    @property
    def feedline_ids(self) -> List[IFeedlineID]:
        """:return: All feedline-ID's in device layer."""
        return self._surface_code_layer.feedline_ids
    # endregion

    # region IConnectivityLayer Interface Properties
    @property
    def qubit_ids(self) -> List[IQubitID]:
        """:return: (All) qubit-ID's in device layer."""
        return self._surface_code_layer.qubit_ids

    @property
    def edge_ids(self) -> List[IEdgeID]:
        """:return: (All) edge-ID's in device layer."""
        return self._surface_code_layer.edge_ids
    # endregion

    # region Class Constructor
    def __init__(self, gate_sequences: List[GateSequenceLayer], parity_group_z: List[IParityGroup], parity_group_x: List[IParityGroup], logical_observables: Optional[List[ILogicalObservable]] = None, surface_code_layer: ISurfaceCodeLayer = Surface17Layer()):
        self._gate_sequences: List[GateSequenceLayer] = gate_sequences
        self._parity_group_z: List[IParityGroup] = parity_group_z
        self._parity_group_x: List[IParityGroup] = parity_group_x
        if logical_observables is None:
            logical_observables = []
        self._logical_observables: Dict[StabilizerType, ILogicalObservable] = {
            logical_observable.observable_basis: logical_observable
            for logical_observable in logical_observables
        }
        self._surface_code_layer: ISurfaceCodeLayer = surface_code_layer
    # endregion

    # region IGenericSurfaceCodeLayer Methods
    def get_gate_sequence_indices(self, parity_group: IParityGroup) -> List[int]:
        """
        :return: Array-like of gate-sequence indices corresponding to parity-group edge-ID's.
        Returns an empty list if parity-group is not present.
        """
        # Guard clause, if parity-group is not present, return empty list
        if parity_group not in self.parity_group_x + self.parity_group_z:
            return []
        edge_ids: List[IEdgeID] = parity_group.edge_ids
        result: List[int] = []
        for gate_sequence_index, gate_sequence in enumerate(self.gate_sequences):
            contains_any_edge: bool = any([edge_id in gate_sequence.edge_ids for edge_id in edge_ids])
            if contains_any_edge:
                result.append(gate_sequence_index)
                continue

        return result

    def get_logical_observable(self, basis: StabilizerType) -> ILogicalObservable:
        """:return: Logical observable corresponding to basis."""
        default_fallback: bool = basis not in self._logical_observables
        if default_fallback:
            warnings.warn(f"Logical observable for basis {basis.name} is not defined in GenericSurfaceCode. Defaulting to {StabilizerType.STABILIZER_Z.name} for all data qubit ID's.")
            return LogicalObservable(
                observable_basis=StabilizerType.STABILIZER_Z,
                data_qubit_projections={
                    data_qubit_id: StabilizerType.STABILIZER_Z
                    for data_qubit_id in self.data_qubit_ids
                }
            )
        return self._logical_observables[basis]
    # endregion

    # region IGateSequenceLayer Interface Methods
    def get_gate_sequence_at_index(self, index: int) -> GateSequenceLayer:
        """:return: Gate-sequence object based on round index."""
        gate_sequences: List[GateSequenceLayer] = self._gate_sequences
        try:
            gate_sequence: GateSequenceLayer = gate_sequences[index]
            return gate_sequence
        except IndexError:
            raise ElementNotIncludedException(f"Index: {index} is out of bounds for gate-sequence of length: {len(gate_sequences)}.")

    def get_gate_sequence_from_element(self, element: IEdgeID) -> GateSequenceLayer:
        """:return: Gate-sequence layer of which edge element is part of."""
        gate_sequences: List[GateSequenceLayer] = self._gate_sequences
        # Assumes element is part of only a single flux-dance layer
        for gate_sequence in gate_sequences:
            if gate_sequence.contains(element=element):
                return gate_sequence
        raise ElementNotIncludedException(f"Element: {element} is not included in any gate-sequence layer.")
    # endregion

    # region ISurfaceCodeLayer Interface Methods
    def get_parity_group(self, element: Union[IQubitID, IEdgeID]) -> List[IParityGroup]:
        """:return: Parity group(s) of which element (edge- or qubit-ID) is part of."""
        result: List[IParityGroup] = []
        # Assumes element is part of only a single parity group
        for parity_group in self.parity_group_x + self.parity_group_z:
            if parity_group.contains(element=element):
                result.append(parity_group)
        return result

    def get_frequency_group_identifier(self, element: IQubitID) -> FrequencyGroupIdentifier:
        """:return: Frequency group identifier based on qubit-ID."""
        return self._surface_code_layer.get_frequency_group_identifier(element=element)
    # endregion

    # region IDeviceLayer Interface Methods
    def get_connected_qubits(self, feedline: IFeedlineID) -> List[IQubitID]:
        """:return: Qubit-ID's connected to feedline-ID."""
        return self._surface_code_layer.get_connected_qubits(feedline=feedline)

    def get_connected_feedline(self, qubit: IQubitID) -> IFeedlineID:
        """:return: Feedline-ID's connected to qubit-ID."""
        return self._surface_code_layer.get_connected_feedline(qubit=qubit)

    def contains(self, element: Union[IFeedlineID, IQubitID, IEdgeID]) -> bool:
        """:return: Boolean, whether element is part of device layer or not."""
        return self._surface_code_layer.contains(element=element)
    # endregion

    # region IConnectivityLayer Interface Methods
    def get_neighbors(self, qubit: IQubitID, order: int = 1) -> List[IQubitID]:
        """
        Requires :param order: to be higher or equal to 1.
        :return: qubit neighbors separated by order. (order=1, nearest neighbors).
        """
        return self._surface_code_layer.get_neighbors(qubit=qubit, order=order)

    def get_edges(self, qubit: IQubitID) -> List[IEdgeID]:
        """:return: All qubit-to-qubit edges from qubit-ID."""
        return self._surface_code_layer.get_edges(qubit=qubit)
    # endregion
